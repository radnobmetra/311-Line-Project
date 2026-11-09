"""
Copy of 311-line-project/evaluation_handling.py. 
Needed for remote_chat_frontend.py. 
"""

import logging
from collections import defaultdict
from agentplatform import types
from .session_handling import (
    list_events, PROJECT_ID
)

# must match the agent_id in your config
AGENT_ID = "sacramento_311_agent"

def evaluate_completed_session(session_id: int):
    """
    pulls a completed session, converts its history, and runs google's evaluation.
    """
    try:
        #get all events using partner's list_events function
        events = list_events(session_id)
        
        if not events:
            return None
            
        #sort events
        ordered_events = sorted(events, key=lambda event: event.timestamp)
        
        # group by invocation_id to link user requests with agent responses
        groups = defaultdict(list)
        first_timestamp = {}
        
        for event in ordered_events:
            groups[event.invocation_id].append(event)
            first_timestamp.setdefault(event.invocation_id, event.timestamp)
            
        #  build the turns required by google's evaluator
        turns = []
        for turn_index, invocation_id in enumerate(sorted(groups, key=first_timestamp.get)):
            eval_events = []
            for event in sorted(groups[invocation_id], key=lambda e: e.timestamp):                
                eval_author = AGENT_ID if event.author == "agent" else event.author
                eval_events.append(
                    types.evals.AgentEvent(
                        author=eval_author,
                        content=event.content,
                    )
                )
                
            turns.append(
                types.evals.ConversationTurn(
                    turn_index=turn_index,
                    turn_id=invocation_id,
                    events=eval_events,
                )
            )
            
        # create the agent data payload
        agent_data = types.evals.AgentData(
            agents={
                AGENT_ID: types.evals.AgentConfig(
                    agent_id=AGENT_ID,
                    instruction="sacramento 311 helpful assistant" 
                )
            },
            turns=turns,
        )
        
       # create a dedicated evaluation client using a supported region
        import agentplatform
        eval_client = agentplatform.Client(
            project=PROJECT_ID, 
            location="us-west1"
        )
        
        result = eval_client.evals.evaluate(
            dataset=types.EvaluationDataset(
                eval_cases=[
                    types.EvalCase(
                        eval_case_id=str(session_id),
                        agent_data=agent_data,
                    )
                ]
            ),
            metrics=[types.RubricMetric.MULTI_TURN_TASK_SUCCESS],
        )
        
        # extract the score and reasoning
        case_result = result.eval_case_results[0]
        metric_result = case_result.response_candidate_results[0].metric_results["multi_turn_task_success_v1"]
        
        evaluation_record = {
            "score": metric_result.score,
            "rubric_verdicts": metric_result.rubric_verdicts,
            "metric_version": metric_result.metric_name,
            "session_id": session_id
        }
        
        return evaluation_record
        
    except Exception as e:
        logging.error(f"evaluation failed for session {session_id}: {e}")
        return None

def calculate_final_outcome(eval_score, user_feedback):
    if not user_feedback:
        return "UNCLEAR"
        
    feedback = user_feedback.lower()
    
    if (eval_score > 0.7 and feedback == "thumbs_down") or \
       (eval_score < 0.4 and feedback == "thumbs_up"):
        return "UNCLEAR"
        
    if eval_score > 0.7 and feedback == "thumbs_up":
        return "HELPED"
        
    if eval_score < 0.4 or feedback == "thumbs_down":
        return "NOT_HELPED"
        
    return "UNCLEAR"