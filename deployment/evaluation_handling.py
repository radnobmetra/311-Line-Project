import logging
from collections import defaultdict
from agentplatform import types
import session_handling 
from user_feedback_handling import list_session_feedback
import json

# must match the agent_id in your config
AGENT_ID = "sacramento_311_agent"

def evaluate_completed_session(session_id: int):
    """
    pulls a completed session, converts its history, and runs google's evaluation.
    """
    try:
        #get all events using partner's list_events function
        events = session_handling.list_events(session_id)
        
        if not events:
            return None

        # Never re-evaluate a session with saved results.
        if any(
            event.author == "eval_author"
            for event in events
        ):
            logging.info(
                "Session %s already has evaluation results.",
                session_id
            )
            return None
            
        #sort events
        ordered_events = sorted(
            (
                event for event in events
                if event.author not in (
                    "session_timeout",
                    "eval_author",
                    "evaluation_skipped",
                    "evaluation_attempted",
                    "evaluation_error",
                    "timer_diagnostic",
                    "user_feedback",
                    "system",
                )
                and event.invocation_id
                and event.content is not None
            ),
            key=lambda event: event.timestamp
        )
        if not ordered_events:
            return None
        
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
            
        # Build configurations for the agents actually
        # present in this conversation.
        agent_ids = {
            AGENT_ID if event.author == "agent" else event.author
            for event in ordered_events
            if event.author != "user"
        }

        agent_configs = {
            agent_id: types.evals.AgentConfig(
                agent_id=agent_id
            )
            for agent_id in agent_ids
        }

        agent_data = types.evals.AgentData(
            agents=agent_configs,
            turns=turns,
        )
        
        # create a dedicated evaluation client using a supported region
        import agentplatform
        eval_client = agentplatform.Client(
            project=session_handling.PROJECT_ID, 
            location="us-west1"
        )

        # Only one worker may run a paid evaluation.
        if not session_handling.claim_evaluation(
            str(session_id)
        ):
            logging.info(
                "Skipping evaluation for unclaimed session %s",
                session_id
            )
            return None

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

        # Avoid saving another combined outcome if this session already has an evaluation marker
        already_evaluated = any(
            event.author == "eval_author"
            for event in events
        )

        if not already_evaluated:

            save_combined_session_results(
                str(session_id),
                evaluation_record
            )

        return evaluation_record

        
    except Exception:
        logging.exception(
            "Evaluation failed for session %s",
            session_id
        )
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

def summarize_session_feedback(session_id: str):
    """
    Summarize feedback stored as managed session events.
    Only the latest rating for each response/user pair counts.
    Does not call Google's Feedback Entries API.
    """

    latest_ratings = {}

    # list_events() already returns events in timestamp order.
    events = session_handling.list_events(str(session_id))

    for event in events:
        if event.author != "user_feedback":
            continue

        content = getattr(event, "content", None)
        parts = getattr(content, "parts", None) or []

        for part in parts:
            text = getattr(part, "text", None)

            if not text:
                continue

            try:
                data = json.loads(text)
            except (TypeError, ValueError):
                logging.warning(
                    "Invalid feedback event in session %s",
                    session_id,
                )
                continue

            if not isinstance(data, dict):
                continue

            event_id = data.get("event_id")
            user_id = data.get("user_id")
            rating = data.get("rating")

            if (
                not event_id
                or not user_id
                or rating not in ("up", "down")
            ):
                continue

            key = (str(event_id), str(user_id))

            # Newer events overwrite older ratings.
            latest_ratings[key] = rating

    thumbs_up = sum(
        rating == "up"
        for rating in latest_ratings.values()
    )

    thumbs_down = sum(
        rating == "down"
        for rating in latest_ratings.values()
    )

    if thumbs_up > thumbs_down:
        overall_rating = "thumbs_up"
    elif thumbs_down > thumbs_up:
        overall_rating = "thumbs_down"
    else:
        overall_rating = None

    return {
        "thumbs_up": thumbs_up,
        "thumbs_down": thumbs_down,
        "rating": overall_rating,
    }

def combine_session_results(session_id: str, eval_results: dict):
    """
    Combine AI evaluation results with real user feedback.

    Returns the individual and combined results
    without saving anything to Google Cloud.
    """

    if not eval_results or eval_results.get("score") is None:
        raise ValueError("AI evaluation score is unavailable.")

    # Retrieve the session's actual user feedback
    feedback = summarize_session_feedback(session_id)

    # Use the existing outcome calculation
    final_outcome = calculate_final_outcome(
        eval_score=eval_results["score"],
        user_feedback=feedback["rating"]
    )

    return {
        "session_id": str(session_id),
        "ai_evaluation": {
            "score": eval_results["score"]
        },
        "user_feedback": feedback,
        "final_outcome": final_outcome
    }


def save_combined_session_results(session_id: str, eval_results: dict):
    """
    Combine AI evaluation and user feedback,
    then save the results as a Google Cloud session event.
    """

    combined_results = combine_session_results(
        session_id,
        eval_results
    )

    # Save individual and combined results together
    event_data = {
        "ai_evaluation": combined_results["ai_evaluation"],
        "user_feedback": combined_results["user_feedback"],
        "final_outcome": combined_results["final_outcome"]
    }

    success = session_handling.add_custom_event(
        author="eval_author",
        custom_data=json.dumps(event_data),
        session_ID=session_id
    )

    if success is not True:
        raise RuntimeError(
            f"Failed to save evaluation results for session {session_id}"
        )

    return combined_results