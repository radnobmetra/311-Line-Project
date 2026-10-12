from google.adk.agents import LlmAgent
from ..config import MODEL
from google.adk.agents.callback_context import CallbackContext
from google.genai import types  # For types.Content
from google.genai.types import Content
from typing import Optional

#The conversation outcome is saved to session state under key outcome_label.
#The session_reviewer agent is called by the end_conversation agent.
#If outcome_label has already been set by another tool, this agent does not run. 
#Otherwise, it retrieves the conversation history and assigns it a label.

def init_and_skip_if_possible (callback_context: CallbackContext) -> Optional[Content]:
    """
    Retrieves the conversation history. 
    Args:
        callback_context(CallbackContext): The ADK callback context.
    Returns:
        conversation_history(str): the conversation history.
    """

    #if outcome_label has been set by another tool or agent, skip session_reviwer execution to save resources

    if "outcome_label" in callback_context.state:
        return Content(
            parts=[
                types.Part(text=f"Outcome label exists.")
            ],
            role="model",  # Assign model role to the overriding response
        )

    #if session_reviewer will run, retrieve the conversation history

    conversation_history = " "
    
    for event in callback_context._invocation_context.session.events:

        #event is user input message 
        if event.author == 'user':
            conversation_history += "user: " + event.content.parts[0].text + "\n"

        #event is agent's response to user
        elif event.is_final_response():
            if event.content:
                if event.content.parts:
                    if event.content.parts[0].text:
                        conversation_history += event.author + ": " + event.content.parts[0].text + "\n"

    if conversation_history == " ":
        conversation_history = "There was an error retrieving the conversation history."

    callback_context.state["conversation_record"] = conversation_history

    return None



session_reviewer = LlmAgent(
    model=MODEL,
    name="SessionReviewerAgent",
    description="Reviews the outcome of the conversation when the conversation has ended.",
    instruction="""
        You review a conversation and classify its outcome.

        Conversation record:
        {conversation_record}

        Review the conversation history and classify it into exactly one of these labels:

        -"User Helped"
            Use only if the agents helped the user.
            This label applies when the agents successfully answer a user's question or retrieve the status of a ticket.
        
        -"Unable to help"
            Use only if the agents did not help the user.

        -"session timeout"
            Use only if other labels do not apply.
        
        Apply exactly one label to the conversation.
        
""",

before_agent_callback = init_and_skip_if_possible,
output_key = "outcome_label"
)
