from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent, InvocationContext
from google.adk.events import Event
from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content, Part
from typing import AsyncGenerator
from ..config import MODEL, QA_INSTRUCTION
from .tools.lookup import search_docs


def save_search_result(tool, args, tool_context: ToolContext, tool_response):
    if getattr(tool, "name", "") == "search_docs":
        tool_context.state["lookup_query"] = args.get("query", "")
        tool_context.state["search_results"] = tool_response
    return None

qa_draft_agent = LlmAgent(
    model=MODEL,
    name="QAAgent",
    description="Returns answers to general questions.",
    instruction=QA_INSTRUCTION,
    tools=[search_docs],
    after_tool_callback=save_search_result,
    output_key="qa",
)

qa_reviewer_agent = LlmAgent(
    model=MODEL,
    name="QAReviewerAgent",
    description="Checks whether the QA answer is acceptable.",
    instruction='''
        You are a strict reviewer.
        
        User question:
        {user_query}

        Retrieved document results:
        {search_results}

        Draft answer:
        {qa}

        Return exactly one word:
        - pass -> only if the answer is directly responsive AND supported by the retrieved documents
        - fail -> if the answer is unsupported, vague, speculative, generic, missing key details, or the documents do not support it

        Be strict.
        Output only: pass or fail''',
    output_key="qa_review",
)

class ValidateQA(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("qa_review", "fail")
        answer = ctx.session.state.get("qa", "")

        if status == "pass":
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=answer)])
            )
        else:
            yield Event(
                author=self.name,
                content=Content(parts=[Part(
                    text="I'm sorry, I couldn't produce a reliable answer from the available documents."
                )])
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