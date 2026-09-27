import asyncio
import os
import uuid

import pandas as pd
import vertexai
from vertexai.evaluation import (
    EvalTask,
    PointwiseMetric,
    PointwiseMetricPromptTemplate,
)

from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from google.cloud import aiplatform
from google.oauth2 import service_account

from my_agent.subagents.pothole_reporting import pothole_report_draft_agent

eval_session_service = InMemorySessionService()

# Copied over from .env
PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
SERVICE_ACCOUNT_FILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
EXPERIMENT_NAME = "POTHOLE_EVAL"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)

aiplatform.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials,
)

async def run_pothole_async(prompt: str) -> dict:
    # Unique user ID
    user_id = f"eval-user-{uuid.uuid4().hex}"

    session = await eval_session_service.create_session(
        app_name=EXPERIMENT_NAME,
        user_id=user_id,
    )
    # Calls the pothole agent
    runner = Runner(
        agent=pothole_report_draft_agent,
        app_name=EXPERIMENT_NAME,
        session_service=eval_session_service,
    )
    # Packs the user's incoming input
    user_message = Content(
        role="user",
        parts=[Part(text=prompt)],
    )
    final_response = ""
    trajectory = []
    # Asynchronous event loop
    async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=user_message):
        # Any tool and function calls
        for function_call in event.get_function_calls():
            trajectory.append({
                    "tool_name": function_call.name,
                    "tool_input": dict(function_call.args or {}),
                })
        # Final responses
        if event.is_final_response() and event.content:
            text_parts = []

            for part in event.content.parts or []:
                text = getattr(part, "text", None)

                if text:
                    text_parts.append(text)

            if text_parts:
                final_response = "".join(text_parts).strip()
    # If no response from the pothole agent
    if not final_response:
        raise RuntimeError(
            f"Pothole returned no final response for prompt: {prompt}"
        )
    # The format Google's agent evaluator expects from a custom agent function
    return {
        "response": final_response,
        "predicted_trajectory": trajectory,
    }

async def generate_eval_responses(eval_dataset):
    responses = []
    trajectories = []
    # For each prompt, the evaluator will respond accordingly
    for prompt in eval_dataset["prompt"]:
        print(f"\nPROMPT: {prompt}")

        result = await run_pothole_async(prompt)

        responses.append(result["response"])
        trajectories.append(result["predicted_trajectory"])

        print(f"RESPONSE: {result['response']}")

    eval_dataset = eval_dataset.copy()
    eval_dataset["response"] = responses
    eval_dataset["predicted_trajectory"] = trajectories

    return eval_dataset

# 10 prompts to simulate user inputs.
datasetPrompts = [
    "I wish to report a pothole I found.",
    "The pothole is located on 6000 J Street, Sacramento.",
    "Here is an image of the pothole I would like to report.",
    "How can I get a picture of the pothole for a report?",
    "Where do I get the location of the pothole?",
    "I have a pothole located in 1234 Rd in Nevada.",
    "I don't have an image of the pothole now. Can I report it later?",
    "Cancel report",
    "I hit a pothole and may have damaged my car's suspension",
    "What is the weather looking like today?"
]
# 10 references that tells the evaluator what to look for in the assistant's response.
datasetReferences = [
    (
        "The user wishes to open a new pothole report. The "
        "assistant should ask for the location of the "
        "pothole and a picture attached with it."
    ),
    (
        "When only given a valid address or street name, the "
        "assistant should prompt the user for an image of the "
        "pothole to complete the report."
    ),
    (
        "The user has supplied an image of the pothole. The "
        "assistant should now ask for the address or street "
        "name of the pothole to complete the report."
    ),
    (
        "The assistant should inform the user to get a picture "
        "of it with their smartphone and from a safe distance from "
        "traffic."
    ),
    (
        "The assistant may suggest a street name, nearby buildings, "
        "or any useful means of getting the pothole's location."
    ),
    (
        "If the given address is outside of Sacramento or California, "
        "the assistant should let the user know that it can only "
        "take locations inside the city of Sacramento."
    ),
    (
        "The user requests to make a pothole report later, and "
        "the assistant should say that it is okay to make a report "
        "later."
    ),
    (
        "The user's wishes to cancel their pothole report. "
        "The assistant should dismiss any ongoing report."
    ),
    (
        "This is a pothole report agent, not a mechanic. The "
        "assistant should inform the user that they can report "
        "a pothole here."
    ),
    (
        "The user's input is completely unrelated. The assistant "
        "should ask them if they wish to report a pothole in the "
        "road."
    )
]
eval_dataset = pd.DataFrame({
    "prompt": datasetPrompts,
    "reference": datasetReferences,
})

# Pointwise Metric that sets the conditions for success (1.0) and failure (0.0).
pothole_text_quality = PointwiseMetric(
    metric = "pothole_text_quality",
    metric_prompt_template = PointwiseMetricPromptTemplate(
        criteria = {
            "completion": (
                "Determine whether he response is straightforward and fairly accurate to the reference."
                "Thus, the response does not have to be word-for-word, but achieve a similar intention."
            )
        },
        rating_rubric = {
            "success": "The response performs well on the completion criteria.",
            "failure": "The response fails on the completion criteria.",
        },
        input_variables=[
            "prompt",
            "response",
            "reference",
        ],
    ),
)

# Main function to run the evaluation
if __name__ == "__main__":

    print("[Running Pothole Evaluation...]\n")

    eval_dataset_with_responses = asyncio.run(
        generate_eval_responses(eval_dataset)
    )

    # Send those responses to Google's evaluation service
    print("\n[Running Google evaluation...]\n")

    eval_result = EvalTask(
        dataset = eval_dataset_with_responses,
        metrics = [pothole_text_quality],
        experiment = "pothole-test"
    ).evaluate()
    results = eval_result.metrics_table

    # Organizes results into a table
    clean_results = results[["prompt",
                             "reference",
                             "response",
                             "pothole_text_quality/score",
                             "pothole_text_quality/explanation"
                             ]].copy()

    # Renames the respective columns of the results table.
    clean_results = clean_results.rename(
        columns={
            "prompt": "Prompt",
            "reference": "Expected Response",
            "response": "Actual Response",
            "pothole_text_quality/score": "Score",
            "pothole_text_quality/explanation": "Evaluator Explanation",
        }
    )

    # Terminal Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Tests run: {len(clean_results)}")
    print(
        f"Average score: "
        f"{clean_results['Score'].mean():.2f}"
    )
    print(
        f"Passed: "
        f"{(clean_results['Score'] == 1).sum()}"
        f"/{len(clean_results)}"
    )

    # Terminal Detailed Results
    print("\nDETAILED RESULTS")
    for i, row in clean_results.iterrows():
        print("\n" + "=" * 80)
        print(f"TEST {i + 1}")
        print("=" * 80)
        print(f"\nPROMPT:\n{row['Prompt']}")
        print(f"\nEXPECTED:\n{row['Expected Response']}")
        print(f"\nACTUAL RESPONSE:\n{row['Actual Response']}")
        print(f"\nSCORE: {row['Score']}")
        print(
            f"\nEVALUATOR EXPLANATION:\n"
            f"{row['Evaluator Explanation']}"
        )

    # Save results to a new directory, if it doesn't already exists.
    results_dir = Path(__file__).resolve().parent / "evaluation_results"
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "pothole_eval_results.csv"
    markdown_path = results_dir / "pothole_eval_results.md"

    # Save CSV
    clean_results.to_csv(
        csv_path,
        index=False,
    )

    # Save markdown report to the results_dir
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write("Pothole Evaluation Results\n\n")
        f.write("=== Summary ===\n")
        f.write(f"Tests Run: {len(clean_results)}\n")
        f.write(f"Average Score: {clean_results['Score'].mean():.2f}\n")
        f.write(
            f"Passed: "
            f"{(clean_results['Score'] == 1).sum()}"
            f"/{len(clean_results)}\n\n"
        )
        for i, row in clean_results.iterrows():
            f.write(f"=== TEST #{i + 1} ===\n")
            f.write("Prompt:\n")
            f.write(f">{row['Prompt']}\n\n")
            f.write("Expected Response:\n")
            f.write(f">{row['Expected Response']}\n\n")
            f.write("Actual Response:\n")
            f.write(f">{row['Actual Response']}\n\n")
            f.write("Score:\n")
            f.write(f">{row['Score']}\n\n")
            f.write("Evaluator Explanation:\n")
            f.write(f">{row['Evaluator Explanation']}\n\n")
        
    print(f"\nSaved CSV results to:\n{csv_path}")
    print(f"\nSaved readable report to:\n{markdown_path}")
