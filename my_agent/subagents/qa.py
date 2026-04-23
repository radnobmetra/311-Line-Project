from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent, InvocationContext
from google.adk.events import Event
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from typing import AsyncGenerator, Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from ..config import MODEL, QA_INSTRUCTION
from .tools.lookup import search_knowledge_tool


def save_search_result(tool, args, tool_context: ToolContext, tool_response):
    # Grabs the search query and results
    if getattr(tool, "name", "") == "search_knowledge_tool":
        tool_context.state["lookup_query"] = args.get("query", "")
        tool_context.state["search_results"] = tool_response
    return None

def save_user_question(callback_context: CallbackContext,llm_request: LlmRequest,) -> Optional[LlmResponse]:
    # Walk backward through request contents to find the latest user text part
    user_question = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if getattr(content, "role", None) == "user" and getattr(content, "parts", None):
                for part in content.parts:
                    text = getattr(part, "text", None)
                    if text:
                        user_question = text
                        break
            if user_question:
                break

    callback_context.state["user_question"] = user_question
    return None

qa_draft_agent = LlmAgent(
    model=MODEL,
    name="QAAgent",
    description="Returns answers to general questions.",
    instruction=QA_INSTRUCTION,
    tools=[search_knowledge_tool],
    before_model_callback=save_user_question,
    after_tool_callback=save_search_result,
    output_key="qa",
)

qa_reviewer_agent = LlmAgent(
    model=MODEL,
    name="QAReviewerAgent",
    description="Checks whether the QA answer is acceptable.",
    instruction='''
        You are a strict reviewer.
        
        Original user question:
        {user_question}

        Search query used:
        {lookup_query}

        Retrieved document results:
        {search_results}

        Draft answer:
        {qa}

        Classify the draft answer into exactly one of these labels:

        - pass
            Use only if the answer is directly responsive and supported by the retrieved documents.

        - pass_with_clarification
            The answer is supported and reasonably helpful, but the user's question is broad, vague, or underspecified, so the final response should also ask the user to clarify or narrow the topic.

        - unsupported_answer
            Use if the answer is unsupported, speculative, vague, generic, incomplete, or misses important details that the documents do contain.

        - emergency
            Use if the user appears to describe an emergency, imminent danger, active crime, urgent medical issue, fire, immediate safety threat, or another situation that should be directed to 911.

        - no_docs_found
            Use if the retrieved documents do not contain relevant information needed to answer the question.

        - out_of_jurisdiction
            Use if the user's question is outside the jurisdiction or scope of Sacramento city services, even if the draft tried to answer it.

        - ambiguous
            Use if the user's question is too unclear to answer reliably from the documents.

        Be strict.
        Return exactly one label and nothing else:
            pass
            pass_with_clarification
            unsupported_answer
            emergency
            no_docs_found
            out_of_jurisdiction
            ambiguous''',
    output_key="qa_review",
)

clarifier_agent = LlmAgent(
    model=MODEL,
    name="ClarifierAgent",
    description="Generates a brief clarification question when the user's request is vague.",
    instruction='''
        You generate a short, helpful clarification follow-up.

        Review result:
        {qa_review}

        Original user question:
        {user_question}

        Search query used:
        {lookup_query}

        Draft answer:
        {qa}


        write 1-2 sentences that:
        - briefly acknowledge the topic
        - ask the user to clarify what specifically they want
        - optionally suggest a few relevant directions (based on the question), but do not assume too much

        Do NOT repeat the full answer.
        Do NOT be verbose.
        Do NOT hallucinate specific policies.

        Example style:
        "Could you clarify what specifically you'd like to know about [topic]? I can help with [...]."
        ''',
    output_key="clarification",
)

class ValidateQA(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("qa_review", "fail")
        answer = ctx.session.state.get("qa", "")


        if status == "pass":
            final_answer = answer
            if not final_answer.endswith("?"):
                final_answer += "\n\nDid that answer your question?"
            else:
                final_answer += "\n\nDid that help?"
        elif status == "unsupported_answer":
            final_answer = (
                "I couldn't produce a reliable answer from the available city documents."
            )
        elif status == "no_docs_found":
            final_answer = (
                "I couldn't find information about that in the available city documents."
            )
        elif status == "out_of_jurisdiction":
            final_answer = (
                "That appears to be outside the scope of Sacramento city services, so I can't answer it from the available city documents."
            )
        elif status == "emergency":
            final_answer = (
                "This sounds like an emergency. Please call 911 right away."
            )
        elif status == "ambiguous":
            final_answer = (
                "I need a little more detail to answer that. Please rephrase your question and include the Sacramento city service or issue you're asking about."
            )
        elif status == "pass_with_clarification":
            async for _ in clarifier_agent.run_async(ctx):
                pass

            clarification = ctx.session.state.get("clarification", "").strip()
            final_answer = answer
            if clarification:
                final_answer += "\n\n" + clarification
            else:
                final_answer += "\n\nCould you clarify what you’d like to know?"
        else:
            final_answer = (
                "I couldn't produce a reliable answer from the available city documents."
            )

        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=final_answer)])
        )



validate_qa_agent = ValidateQA(
    name="ValidateQAAgent",
    description="Returns the QA answer only if it passed review.",
)
    
qa_agent = SequentialAgent(
    name="QAWorkflowAgent",
    sub_agents=[
        qa_draft_agent,
        qa_reviewer_agent,
        validate_qa_agent,
    ],
)