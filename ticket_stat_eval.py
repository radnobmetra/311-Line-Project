import pandas as pd
import vertexai
from vertexai.evaluation import EvalTask, PointwiseMetric, PointwiseMetricPromptTemplate
from google.cloud import aiplatform
from google.oauth2 import service_account

# Import your actual agent
from my_agent.subagents.ticketstatus import ticketstatus_agent

PROJECT_ID = "twiliosacstate"
LOCATION = "us-central1"
EXPERIMENT_NAME = "ticketstatus-agent-evaluation"
SERVICE_ACCOUNT_FILE = "sa-key.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE
)

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)

# 1. Define your evaluation criteria (tailored for a support ticket agent)
ticket_quality_metric = PointwiseMetric(
    metric="ticket_agent_quality",
    metric_prompt_template=PointwiseMetricPromptTemplate(
        input_variables=["prompt", "response"],
        criteria={
            "helpfulness": (
                "The response directly addresses the user's ticket status inquiry, provides clear information, and maintains an engaging, polite tone. If no ticket number is provided, it prompts user to provide a ticket number or tells the user no ticket of that number exists if invalid."
            ),
            "accuracy_and_clarity": (
                "The response avoids vague language and gives concrete details about the status of the support request."
            ),
        },
        rating_rubric={
            "1": "The response is clear, highly helpful, and meets all criteria.",
            "0.5": "The response is somewhat helpful but lacks specific detail or clarity.",
            "0": "The response is unhelpful, vague, or fails to address the user.",
        },
    ),
)

# 2. Create a test dataset with real prompts your agent expects
eval_prompts = [
    "Can you check the status of my ticket 241025-2719636?",
    #"What is happening with my login issue ticket?",
    #"Hey there, any updates on my request?",
]

# 3. Dynamically generate responses using the proper ADK execution method
from google.adk.runners import Runner  # Or check your local adk import path for Runner

generated_responses = []
for prompt in eval_prompts:
    try:
        # ADK agents typically require a Runner to manage the session/state loop.
        # Alternatively, check your project's main.py or runner files to see how 
        # local queries are executed, or pass it to an active runner session:
        runner = Runner(agent=ticketstatus_agent, app_name="eval_session")
        
        # Run synchronously or call your agent's chat handling function
        # (If your setup uses an async runner, use asyncio.run(runner.run_async(...)))
        response_obj = runner.run(input=prompt) 
        
        response_text = str(response_obj)
    except Exception as e:
        # Keep this print temporarily so you can see if any other error pops up
        print(f"Execution Error: {e}")
        response_text = "Error executing agent."
        
    generated_responses.append(response_text)

print("Actual generated response text:", generated_responses)
# 4. Build the evaluation DataFrame containing both prompts and generated responses
eval_dataset = pd.DataFrame({
    "prompt": eval_prompts,
    "response": generated_responses,
})


# 5. Run the Vertex AI Evaluation Task
eval_task = EvalTask(
    dataset=eval_dataset,
    metrics=[ticket_quality_metric],
    experiment=EXPERIMENT_NAME
)

pointwise_result = eval_task.evaluate()

# 6. Output the results
print("--- Summary Metrics ---")
print(pointwise_result.summary_metrics)

print("\n--- Detailed Metrics Table ---")
print(pointwise_result.metrics_table)

# Optional: Clean up the experiment run if you don't want to clutter Vertex AI Experiments
aiplatform.ExperimentRun(
    run_name=pointwise_result.metadata["experiment_run"],
    experiment=pointwise_result.metadata["experiment"],
).delete()