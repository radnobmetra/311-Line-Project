import pandas as pd

import vertexai
from vertexai import Client
from vertexai.evaluation import EvalTask, PointwiseMetric, PointwiseMetricPromptTemplate
from google.cloud import aiplatform
from google.oauth2 import service_account

from my_agent.subagents.ticketstatus import ticketstatus_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

PROJECT_ID = "twiliosacstate"
LOCATION = "us-central1"
EXPERIMENT_NAME = "ticket-eval"
SERVICE_ACCOUNT_FILE = "sa-key.json"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE
)

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)

client = Client(project=PROJECT_ID, location=LOCATION)

custom_text_quality = PointwiseMetric(
    metric="custom_text_quality",
    metric_prompt_template=PointwiseMetricPromptTemplate(
        criteria={
            "fluency": (
                "Sentences flow smoothly and are easy to read, avoiding awkward phrasing or run-on sentences. Ideas and sentences connect logically, using transitions effectively where needed."
            ),
            "entertaining": (
                "Short, amusing text that incorporates emojis, exclamations and questions to convey quick and spontaneous communication and diversion."
            ),
        },
        rating_rubric={
            "1": "The response performs well on both criteria.",
            "0.5": "The response is somewhat aligned with both criteria",
            "0": "The response falls short on one criteria",
            "-1": "The response falls short on both criteria",
        },
    ),
)

session_service = InMemorySessionService()

runner = Runner(
    agent=ticketstatus_agent,  # Or your root agent
    app_name=EXPERIMENT_NAME,
    session_service=session_service,
)

prompts = pd.DataFrame({
    "prompt": [
        "I want to find ticket 241025-2719636"
    ]
})
#
#responses = [
    # An example of good custom_text_quality
 #   "Ticket 241025-2719639 is about a homeless encampment blocking a sidewalk at 311 N 16th st, Sacramento. The ticket is solved and currently closed."
#]

generated_responses = []
for prompt in prompts:
  # Create a session and run the agent synchronously/asynchronously as needed
  session_id = session_service.create_session(user_id="eval_user")

eval_dataset = pd.DataFrame({
    "prompt": prompts,
    "response" : generated_responses,
})

eval_task = EvalTask(
    dataset=eval_dataset,
    metrics=[custom_text_quality],
    experiment=EXPERIMENT_NAME
)

pointwise_result = eval_task.evaluate()

print(pointwise_result.summary_metrics)

print(pointwise_result.metrics_table)

aiplatform.ExperimentRun(
    run_name=pointwise_result.metadata["experiment_run"],
    experiment=pointwise_result.metadata["experiment"],
).delete()
