from google.adk.agents import LlmAgent
from ..config import MODEL, QA_INSTRUCTION
from tools.lookup import search_docs

qa_agent = LlmAgent(
    model=MODEL,
    name="QAAgent",
    description="Returns answers to general questions.",
    instruction=QA_INSTRUCTION,
    tools=[search_docs],
    output_key="qa",
)
