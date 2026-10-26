import sys
import json
sys.path.insert(1, "..\\311-Line-Project")

import evaluation_handling
import session_handling

def test_evaluate_completed_session():
    session_id = 7271673476610523136
    eval_results = evaluation_handling.evaluate_completed_session(session_id=session_id)
    
    # pytest 
    assert eval_results is not None
    assert "score" in eval_results
    assert "rubric_verdicts" in eval_results

    # detailed results
    print("\n--- EVALUATION RESULTS ---")
    print(f"Score: {eval_results['score']}")
    print(f"Reasoning: {eval_results['rubric_verdicts']}")
    
    final_outcome = evaluation_handling.calculate_final_outcome(eval_results['score'], user_feedback="thumbs_up")
    print(f"Final Outcome Tag: {final_outcome}")   
    
    session_handling.add_custom_event(author="system", custom_data=json.dumps({"final_outcome": final_outcome}), session_ID=session_id)
    print("Outcome saved to session.")

# for running script w details, use 'python tests/evaluation_handling_test.py'
if __name__ == "__main__":
    test_evaluate_completed_session()

def test_evaluate_given_sessions():
    test_author_name = "John_test"
    sessions_modified = evaluation_handling.evaluate_given_sessions([test_author_name])
    assert sessions_modified == 0