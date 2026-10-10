import sys
sys.path.insert(1, "..\\311-Line-Project")

import evaluation_handling

session_id = 7271673476610523136

print(f"Running Google evaluation on live cloud session: {session_id}...")
eval_results = evaluation_handling.evaluate_completed_session(session_id=session_id)

if eval_results:
    print("\nEvaluation Sucess!")
    print(f"Score: {eval_results['score']}")
    print(f"Reasoning: {eval_results['rubric_verdicts']}")
else:
    print("\nEvaluation returned None. Check the terminal for errors.")