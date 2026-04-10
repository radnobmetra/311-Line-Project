from google.adk.tools.tool_context import ToolContext

def invalid_request_limit_reached(tool_context: ToolContext) -> bool:
    """
    Returns a bool indicating if the user has made too many invalid requests.

    Args:
        tool_context: the ADK tool context.

    Returns:
        A boolean indicating if the user has made too many invalid requests.
        If true: 
            The user has made too many invalid requests. The agent should not assist with the user's request.
        If false:
            The user hasn't made too many invalid requests yet.
    """

    state = tool_context.state          #use tool context and state to store and access the number of invalid requests
    max_num_invalid_requests = 3        #maximum number of unsuccessful requests that user can make before agent redirects them

    #if counter hasn't been created yet, return false

    if "num_invalid_requests" not in state:
        return False
    
    #if user has reached the invalid request limit, return true

    if int(state["num_invalid_requests"]) >= max_num_invalid_requests:
        return True
    
    return False

def update_num_invalid_requests(tool_context: ToolContext):
    """
    Increments the counter of the number of invalid requests made by the user.
    
    Args:
        tool_context: the ADK tool context.
    """

    #use tool context to store and access the number of invalid requests

    state = tool_context.state

    #if counter for invalid requests hasn't been created yet, create a record for it in state

    if "num_invalid_requests" not in state:
        state["num_invalid_requests"] = 0

    #increment counter

    state["num_invalid_requests"] += 1