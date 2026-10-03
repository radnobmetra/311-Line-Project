from pathlib import Path
import os
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_DIR = PROJECT_ROOT / "deployment"

REQUIRED_FILES = [
    "my_agent",
    "timerloop.py",
    "session_manager.py",
    "runtime_app.py",
    "requirements.txt",
    "emergency_cases.json",
]

FORBIDDEN_NAMES = {
    ".env",
    ".venv",
    "sa-key.json",
    "__pycache__",
}


def test_deployment_folder_contains_required_files():
    #deployment source contains required runtime files

    for name in REQUIRED_FILES:
        path = DEPLOYMENT_DIR / name

        assert path.exists(), (
            f"Required deployment source is missing: {path}"
        )

    requirements = DEPLOYMENT_DIR / "requirements.txt"

    assert requirements.stat().st_size > 0, (
        "deployment/requirements.txt exists but is empty"
    )


def test_deployment_folder_excludes_local_and_sensitive_files():
    #local files and secrets are not packaged

    violations = []

    for path in DEPLOYMENT_DIR.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            violations.append(str(path.relative_to(DEPLOYMENT_DIR)))

        if path.suffix == ".pyc":
            violations.append(str(path.relative_to(DEPLOYMENT_DIR)))

    assert not violations, (
        "Deployment folder contains files that must not be deployed:\n"
        + "\n".join(violations)
    )


def test_runtime_entrypoint_imports_from_deployment_folder():
    #deployed entrypoint and overseer import successfully.

    env = os.environ.copy()

    # Prevent this test itself from creating __pycache__ files.
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            (
                "from runtime_app import app; "
                "from my_agent.agent import root_agent; "
                "print(root_agent.name)"
            ),
        ],
        cwd=DEPLOYMENT_DIR,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, (
        "Runtime entrypoint failed to import.\n\n"
        f"STDOUT:\n{result.stdout}\n\n"
        f"STDERR:\n{result.stderr}"
    )

    assert "OverseerAgent" in result.stdout