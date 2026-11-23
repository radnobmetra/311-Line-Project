
import csv
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVAL_SCRIPT = ROOT / "evaluation" / "evaluate_qa.py"
RESULTS_CSV = (
    ROOT / "evaluation" / "evaluation_results" / "qa_eval_results.csv"
)


@pytest.fixture(scope="module")
def qa_results():
    previous_time = (
        RESULTS_CSV.stat().st_mtime_ns
        if RESULTS_CSV.exists() else -1
    )

    # Run the existing Google Q&A evaluation.
    completed = subprocess.run(
        [sys.executable, "-m", "evaluation.evaluate_qa"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        errors="replace",
    )

    assert completed.returncode == 0, (
        f"Q&A evaluation failed:\n"
        f"{completed.stderr[-4000:]}\n"
        f"{completed.stdout[-4000:]}"
    )

    # Make sure a new report was produced.
    assert RESULTS_CSV.is_file(), "Q&A evaluation did not write its CSV results"
    assert RESULTS_CSV.stat().st_mtime_ns > previous_time, (
        "Q&A results were not refreshed"
    )

    with RESULTS_CSV.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 10, "Expected all 10 existing Q&A evaluation cases"

    return {row["Prompt"]: row for row in rows}



def test_qa_on_topic(qa_results):
    question = "How do I report a pothole in Sacramento?"
    row = qa_results[question]

    assert row["Actual Response"].strip()
    assert float(row["Score"]) == 1.0, row["Evaluator Explanation"]

    print("\n--- Q&A: ON TOPIC ---")
    print(f"Question: {question}")
    print(f"Agent response: {row['Actual Response']}")
    print(f"Evaluation score: {row['Score']}")


def test_qa_off_topic(qa_results):
    question = "How do I renew my California driver's license?"
    row = qa_results[question]

    assert row["Actual Response"].strip()
    assert float(row["Score"]) == 1.0, row["Evaluator Explanation"]

    print("\n--- Q&A: OFF TOPIC ---")
    print(f"Question: {question}")
    print(f"Agent response: {row['Actual Response']}")
    print(f"Evaluation score: {row['Score']}")


def test_google_qa_evaluation_occurs(qa_results):
    assert all(
        row["Evaluator Explanation"].strip()
        for row in qa_results.values()
    )

    scores = [float(row["Score"]) for row in qa_results.values()]
    assert all(score in (0.0, 1.0) for score in scores)

    print("\n--- GOOGLE Q&A EVALUATION ---")
    print(f"Questions evaluated: {len(scores)}")
    print(f"Average score: {sum(scores) / len(scores):.2f}")
    print(f"Passing evaluations: {sum(s == 1.0 for s in scores)}/{len(scores)}")

