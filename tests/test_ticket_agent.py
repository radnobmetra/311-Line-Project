import subprocess
import sys
from pathlib import Path


def test_ticket_agent_evaluation():
    test_dir = Path(__file__).resolve().parent
    project_dir = test_dir.parent

    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))

    subprocess.run(
        [sys.executable, str(project_dir / "ticket_eval.py")],
        cwd=project_dir,
        check=True,
    )

    results_file = project_dir / "evaluation_results/ticket_stat_eval_results.md"
    with results_file.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    assert len(lines) >= 6, f"Expected at least 6 lines, got {len(lines)}"
    assert lines[5] == "- Average score: 1.00"