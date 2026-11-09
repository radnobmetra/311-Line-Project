from google.adk.agents import LlmAgent, BaseAgent, InvocationContext
from google.adk.events import Event
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from typing import AsyncGenerator, Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from ..config import MODEL, QA_INSTRUCTION, QA_REVIEWER_INSTRUCTION, QA_CLARIFIER_INSTRUCTION
from .tools.lookup import search_knowledge_tool
from google.adk import Workflow


def save_search_result(tool, args, tool_context: ToolContext, tool_response):
    # Grabs the search query and results
    if getattr(tool, "name", "") == "search_knowledge_tool":
        tool_context.state["lookup_query"] = args.get("query", "")
        tool_context.state["search_results"] = tool_response
    return None

def save_user_question(callback_context: CallbackContext,llm_request: LlmRequest,) -> Optional[LlmResponse]:
    
    # Defaults in case the search tool is not called.
    callback_context.state.setdefault("lookup_query", "")
    callback_context.state.setdefault(
        "search_results",
        "No search was performed."
    )
    
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
    instruction=QA_REVIEWER_INSTRUCTION,
    output_key="qa_review",
)

clarifier_agent = LlmAgent(
    model=MODEL,
    name="ClarifierAgent",
    description="Generates a brief clarification question when the user's request is vague.",
    instruction=QA_CLARIFIER_INSTRUCTION,
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
                final_answer += "\n\nCould you clarify what you'd like to know?"
        else:
            final_answer = (
                "I couldn't produce a reliable answer from the available city documents."
            )

        yield Event(
            author=self.name,
            content=Content(parts=[Part(text=final_answer)]),
            output=final_answer,
        )



validate_qa_agent = ValidateQA(
    name="ValidateQAAgent",
    description="Returns the QA answer only if it passed review.",
)
    
qa_agent = Workflow(
    name="QAWorkflowAgent",
    description="Answers general Sacramento city-service questions using available city documents.",
    input_schema=str,
    edges=[
        ("START", qa_draft_agent, qa_reviewer_agent, validate_qa_agent),
    ],
)