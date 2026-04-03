from google.adk.agents import LlmAgent, SequentialAgent
from ..config import MODEL, GREETING_INSTRUCTION
from overseer import overseer_agent


greeting_agent = LlmAgent(
    model=MODEL,
    name="GreetingAgent",
    description="Greets user at the start of a new session.",
    instruction=GREETING_INSTRUCTION,
)

greet_and_assist_agent = SequentialAgent(
    name="greet_and_assist_agent",
    sub_agents=[greeting_agent, overseer_agent],
    description="A workflow that first greet the user and then assist the user based on their inquiry.",
)
