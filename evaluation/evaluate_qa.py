import asyncio
import os
import uuid

import pandas as pd
import vertexai
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from google.oauth2 import service_account

from vertexai.evaluation import (
    EvalTask,PointwiseMetric,PointwiseMetricPromptTemplate)

from my_agent.subagents import qa_agent
APP_NAME = "my_agent"
eval_session_service = InMemorySessionService()
    
PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
CREDENTIALS = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS)

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)


async def run_qa_async(prompt: str) -> dict:
    """Runs QAWorkflowAgent on a single prompt 
    and returns the final response and tool call trajectory."""

    user_id = f"eval-user-{uuid.uuid4().hex}"

    session = await eval_session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
    )

    runner = Runner(
        agent=qa_agent,
        app_name=APP_NAME,
        session_service=eval_session_service,
    )

    user_message = Content(
        role="user",
        parts=[Part(text=prompt)],
    )

    final_response = ""
    trajectory = []

    async for event in runner.run_async(
        user_id=user_id, session_id=session.id, new_message=user_message,):

        # Capture tool calls.
        for function_call in event.get_function_calls():
            trajectory.append(
                {
                    "tool_name": function_call.name,
                    "tool_input": dict(function_call.args or {}),
                }
            )

        # Capture the final workflow response.
        if event.is_final_response() and event.content:
            text_parts = []

            for part in event.content.parts or []:
                text = getattr(part, "text", None)

                if text:
                    text_parts.append(text)

            if text_parts:
                final_response = "".join(text_parts).strip()

    if not final_response:
        raise RuntimeError(
            f"QA workflow returned no final response for prompt: {prompt}"
        )

    # This is the format Google's agent evaluator expects from a custom agent function.
    return {
        "response": final_response,
        "predicted_trajectory": trajectory,
    }


async def generate_eval_responses(eval_dataset):
    responses = []
    trajectories = []

    for prompt in eval_dataset["prompt"]:
        print(f"\nRunning QA agent for: {prompt}")

        result = await run_qa_async(prompt)

        responses.append(result["response"])
        trajectories.append(result["predicted_trajectory"])

        print(f"Response: {result['response']}")

    eval_dataset = eval_dataset.copy()
    eval_dataset["response"] = responses
    eval_dataset["predicted_trajectory"] = trajectories

    return eval_dataset


# Small test dataset
eval_dataset = pd.DataFrame(
    {
        "prompt": [
            "There is a fire in my apartment right now. What should I do?",
            "How do I renew my California driver's license?",
            "How do I fix it?",
            "What do I do about a rabid dog?",
            "How do I report a pothole in Sacramento?",
            "What are the hours for the Sacramento Public Library?",
            "Can you tell me what Sacramento's parking rules are?",
            "Someone is breaking into my house right now. What should I do?",
            "How do I get a passport in Sacramento?",
            "How do I pay my Sacramento utility bill?",
        ],

        "reference": [
            (
                "The user should be told that this is an emergency "
                "and instructed to call 911 immediately."
            ),
            (
                "The request is outside the scope of Sacramento city "
                "services, so the assistant should explain that it cannot "
                "answer it using the available city documents."
            ),
            (
                "The request is too ambiguous to answer. The assistant "
                "should ask the user for more detail about the Sacramento "
                "city service or issue they are asking about."
            ),
            (
                "The user should be told information about what to do about a rabid dog "
                "using the available Sacramento city documents."
                "The answer should be concise."
            ),
            (
                "The assistant should provide the Sacramento city procedure "
                "for reporting a pothole, based on the available city documents."
            ),
            (
                "The assistant should provide the relevant Sacramento Public "
                "Library hours from the available city documents, if those "
                "documents contain the information."
            ),
            (
                "The question is broad and may require clarification about "
                "which Sacramento parking rules the user means. The assistant "
                "should provide any supported general information and ask the "
                "user to clarify the specific parking issue if necessary."
            ),
            (
                "The user should be told that this is an emergency and "
                "instructed to call 911 immediately."
            ),
            (
                "The assistant should use the available Sacramento city documents to "
                "explain that the Sacramento City Clerk does not process passport "
                "applications and provide any relevant alternative passport application "
                "resources or locations contained in the documents."
            ),
            (
                "The assistant should provide the Sacramento city procedure "
                "for paying a utility bill using the available city documents. "
                "The answer should be directly supported by those documents."
            ),
        ],
    }
)

# Define how Google should judge the answer
qa_quality_metric = PointwiseMetric(
    metric="qa_response_quality",

    metric_prompt_template=PointwiseMetricPromptTemplate(
        criteria={
            "correctness": (
                "Determine whether the response correctly handles the "
                "user's request according to the reference answer. "
                "The response does not need to use the same wording as "
                "the reference. It should be directly responsive and "
                "must not introduce material unsupported information."
            )
        },

        rating_rubric={
            "1": (
                "The response is correct, directly responsive, and "
                "consistent with the expected behavior in the reference."
            ),
            "0": (
                "The response is incorrect, materially incomplete, "
                "unsupported, or inconsistent with the expected behavior."
            ),
        },

        input_variables=[
            "prompt",
            "response",
            "reference",
        ],
    ),
)

# Run evaluation
if __name__ == "__main__":

    #Run QA workflow
    print("Running QA workflow...\n")

    eval_dataset_with_responses = asyncio.run(
        generate_eval_responses(eval_dataset)
    )

    print("\nRESPONSES GENERATED")
    print(
        eval_dataset_with_responses[
            ["prompt", "response", "reference"]
        ].to_string(index=False)
    )

    # Send those responses to Google's evaluation service
    print("\nRunning Google evaluation...\n")

    eval_task = EvalTask(
        dataset=eval_dataset_with_responses,
        metrics=[
            qa_quality_metric,
        ],
    )

    eval_result = eval_task.evaluate()
    results = eval_result.metrics_table


    #clean results for display
    clean_results = results[
    ["prompt","reference",
     "response","qa_response_quality/score",
     "qa_response_quality/explanation",]
     ].copy()

    clean_results = clean_results.rename(
        columns={
            "prompt": "Prompt",
            "reference": "Expected Response",
            "response": "Actual Response",
            "qa_response_quality/score": "Score",
            "qa_response_quality/explanation": "Evaluator Explanation",
        }
    )

    #Terminal Summary
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

    #Terminal Detailed Results
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

    #save results
    results_dir = Path(__file__).resolve().parent / "evaluation_results"
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "qa_eval_results.csv"
    markdown_path = results_dir / "qa_eval_results.md"

    # Save CSV
    clean_results.to_csv(
        csv_path,
        index=False,
    )

    # Save Markdown report
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write("# QA Evaluation Results\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Tests run: {len(clean_results)}\n")
        f.write(f"- Average score: {clean_results['Score'].mean():.2f}\n")
        f.write(
            f"- Passed: "
            f"{(clean_results['Score'] == 1).sum()}"
            f"/{len(clean_results)}\n"
        )
        for i, row in clean_results.iterrows():
            f.write("\n---\n\n")
            f.write(f"## Test {i + 1}\n\n")
            f.write("### Prompt\n\n")
            f.write(f"{row['Prompt']}\n\n")
            f.write("### Expected Response\n\n")
            f.write(f"{row['Expected Response']}\n\n")
            f.write("### Actual Response\n\n")
            f.write(f"{row['Actual Response']}\n\n")
            f.write("### Score\n\n")
            f.write(f"{row['Score']}\n\n")
            f.write("### Evaluator Explanation\n\n")
            f.write(f"{row['Evaluator Explanation']}\n")
        
    print(f"\nSaved CSV results to:\n{csv_path}")
    print(f"\nSaved readable report to:\n{markdown_path}")