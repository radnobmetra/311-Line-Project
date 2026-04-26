from google.adk.agents import Agent
from google.cloud import modelarmor_v1

def validate_user_input(user_input: str) -> dict:
    """
    Use Model Armor to validate all user inputs for security threats.
    
    Args:
        user_input (str): The user input to validate.
        
    Returns:
        dict: Validation result with status and message.
    """
    client = modelarmor_v1.ModelArmorClient()
    request = modelarmor_v1.SanitizeUserPromptRequest(
        name="projects/project-d9b429fa-7589-4021-9af/locations/us-west1/templates/311SMSTextSecurity",
        user_prompt_data={"text": user_input}
    )
    # In the event of network-related error, the agent will catch the
    # exception and return an error message instead of crashing.
    try:
        response = client.sanitize_user_prompt(request=request)
        if response.filter_match_state == "MATCH_FOUND":
            return {
                "status": "error",
                "message": "I'm sorry. Due to security reasons, I am unable to process that request."
            }
        return {
            "status": "success",
            "message": "Input validated."
            }
    except Exception as e:
        return {"status": "error", "message": f"Security Validation Failed: {str(e)}"}

root_agent = Agent(
    name="overseer_agent",
    model="gemini-2.5-flash-preview",
    instruction=(
        "You are an agent whose job is to determine whether the user's input is valid and safe."
    ),
    tools=[validate_user_input],
)