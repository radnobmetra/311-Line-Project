"""
Deploy to Google Agent Runtime.

The deployment source lives in ./deployment.
"""

import importlib.metadata
import os
import subprocess
import sys
from pathlib import Path
import shutil
import dotenv


# PROJECT / ENVIRONMENT
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR
ENV_FILE = PROJECT_DIR / ".env"
SOURCE_DIR = PROJECT_DIR / "deployment"
RUNTIME_FILE = PROJECT_DIR / "runtime_id.txt"

dotenv.load_dotenv(ENV_FILE)


def require_env(name: str) -> str:
    value = os.environ.get(name)

    if not value:
        raise RuntimeError(
            f"Required environment variable is not set: {name}\n"
            f"Expected it to be available from: {ENV_FILE}"
        )

    return value


PROJECT_ID = require_env("GOOGLE_CLOUD_PROJECT")

RUNTIME_LOCATION = os.environ.get(
    "AGENT_RUNTIME_LOCATION",
    "us",
)

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


# CREDENTIALS

# Resolve credentials BEFORE changing cwd.
raw_credentials = Path(
    require_env("GOOGLE_APPLICATION_CREDENTIALS")
).expanduser()

if raw_credentials.is_absolute():
    CREDENTIALS_FILE = raw_credentials.resolve()
else:
    CREDENTIALS_FILE = (
        PROJECT_DIR / raw_credentials
    ).resolve()

if not CREDENTIALS_FILE.is_file():
    raise FileNotFoundError(
        "Service-account key was not found.\n"
        f"Project directory: {PROJECT_DIR}\n"
        f"Value from .env:   {raw_credentials}\n"
        f"Resolved path:     {CREDENTIALS_FILE}"
    )

# Important: make absolute before changing cwd.
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
    CREDENTIALS_FILE
)


# RUNTIME ENVIRONMENT
# Do NOT add GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, or GOOGLE_APPLICATION_CREDENTIALS here
RUNTIME_ENV_VARS = {
    "ELASTIC_API_ENDPOINT": require_env("ELASTIC_API_ENDPOINT"),
    "ELASTIC_API_KEY": require_env("ELASTIC_API_KEY"),
    "SESSION_AGENT_ENGINE_ID": require_env("SESSION_AGENT_ENGINE_ID"),
    "MODEL_LOCATION": os.environ.get(
        "MODEL_LOCATION",
        "us",
    ),
}

if os.environ.get("RANKING_API_REGION"):
    RUNTIME_ENV_VARS["RANKING_API_REGION"] = os.environ[
        "RANKING_API_REGION"
    ]


# SOURCE PACKAGE
SOURCE_PACKAGES = [
    "my_agent",
    "timerloop.py",
    "session_manager.py",
    "runtime_app.py",
    "requirements.txt",
    "emergency_cases.json",
]

REQUIRED_SOURCE_PATHS = [
    SOURCE_DIR / path
    for path in SOURCE_PACKAGES
]

FORBIDDEN_NAMES = {
    ".env",
    "sa-key.json",
    ".venv",
}


def validate_source() -> None:
    print()
    print("=" * 78)
    print("VALIDATING DEPLOYMENT SOURCE")
    print("=" * 78)

    if not SOURCE_DIR.is_dir():
        raise FileNotFoundError(
            f"Deployment folder does not exist: {SOURCE_DIR}"
        )

    # Remove Python cache files so they are never deployed
    for cache_dir in SOURCE_DIR.rglob("__pycache__"):
        shutil.rmtree(cache_dir)

    for pyc_file in SOURCE_DIR.rglob("*.pyc"):
        pyc_file.unlink()

    # Make sure all required source paths exist
    for path in REQUIRED_SOURCE_PATHS:
        if not path.exists():
            raise FileNotFoundError(
                f"Required deployment source is missing: {path}"
            )

    # Reject local-only / sensitive files
    problems = []

    for path in SOURCE_DIR.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            problems.append(path)

        if path.is_file() and path.suffix == ".pyc":
            problems.append(path)

    if problems:
        formatted = "\n".join(
            f"  - {path}"
            for path in problems
        )

        raise RuntimeError(
            "Deployment source contains files that must not be uploaded:\n"
            f"{formatted}"
        )

    # Agent Runtime inline source limit is 8 MB.
    total_bytes = 0

    for source_path in REQUIRED_SOURCE_PATHS:
        if source_path.is_file():
            total_bytes += source_path.stat().st_size
        else:
            total_bytes += sum(
                path.stat().st_size
                for path in source_path.rglob("*")
                if path.is_file()
            )

    total_mb = total_bytes / (1024 * 1024)

    print(f"Source size: {total_mb:.2f} MB")

    if total_mb > 8:
        raise RuntimeError(
            "Deployment source exceeds Agent Runtime's "
            f"8 MB inline-source limit: {total_mb:.2f} MB"
        )

    print("Source files: PASS")

# LOCAL ENTRYPOINT TEST
def validate_entrypoint() -> None:
    print()
    print("=" * 78)
    print("VALIDATING RUNTIME ENTRYPOINT")
    print("=" * 78)

    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            (
                "from runtime_app import app; "
                "print('ENTRYPOINT IMPORT PASS:', "
                "type(app).__name__)"
            ),
        ],
        cwd=SOURCE_DIR,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout.strip())

    if result.returncode != 0:
        if result.stderr:
            print(result.stderr)

        raise RuntimeError(
            "The Runtime entrypoint could not be imported."
        )


# AUTHENTICATION TEST
def verify_authentication() -> None:
    import google.auth
    from google.oauth2 import service_account

    explicit_credentials = (
        service_account.Credentials.from_service_account_file(
            str(CREDENTIALS_FILE),
            scopes=SCOPES,
        )
    )

    adc_credentials, _ = google.auth.default(
        scopes=SCOPES,
    )

    adc_email = getattr(
        adc_credentials,
        "service_account_email",
        None,
    )

    print()
    print("=" * 78)
    print("AUTHENTICATION")
    print("=" * 78)

    print(
        "Expected service account:",
        explicit_credentials.service_account_email,
    )

    print(
        "ADC service account:",
        adc_email,
    )

    if (
        adc_email
        != explicit_credentials.service_account_email
    ):
        raise RuntimeError(
            "ADC is not using the expected service account.\n"
            f"Expected: "
            f"{explicit_credentials.service_account_email}\n"
            f"Actual:   {adc_email}"
        )

    print("Authentication: PASS")


# AGENT RUNTIME METHODS
CLASS_METHODS = [
    {
        "name": "async_create_session",
        "api_mode": "async",
    },
    {
        "name": "async_get_session",
        "api_mode": "async",
    },
    {
        "name": "async_list_sessions",
        "api_mode": "async",
    },
    {
        "name": "async_delete_session",
        "api_mode": "async",
    },
    {
        "name": "async_stream_query",
        "api_mode": "async_stream",
    },
]

# DEPLOY
def main() -> None:
    validate_source()
    validate_entrypoint()
    verify_authentication()

    import agentplatform

    print()
    print("=" * 78)
    print("311 AGENT RUNTIME DEPLOYMENT")
    print("=" * 78)

    print("Project:", PROJECT_ID)
    print("Runtime location:", RUNTIME_LOCATION)
    print("Source:", SOURCE_DIR)

    print(
        "google-cloud-agentplatform:",
        importlib.metadata.version(
            "google-cloud-agentplatform"
        ),
    )

    client = agentplatform.Client(
        project=PROJECT_ID,
        location=RUNTIME_LOCATION,
    )
    # Agent Platform SDK compatibility:
    # New SDK:
    #     client.runtimes.create/update/...

    # Older/compatibility SDK:
    #     client.agent_engines.create/update/...
    if (
        hasattr(client, "runtimes")
        and hasattr(client.runtimes, "update")
    ):
        runtimes_api = client.runtimes
    elif (
        hasattr(client, "agent_engines")
        and hasattr(client.agent_engines, "update")
    ):
        runtimes_api = client.agent_engines
    else:
        raise RuntimeError(
            "Installed Agent Platform SDK does not expose "
            "a supported Runtime deployment API."
        )

    original_dir = Path.cwd()

    try:
        # Change to deployment root before sending source paths
        os.chdir(SOURCE_DIR)

        print()
        print(
            "Deployment working directory:",
            Path.cwd(),
        )

        print()
        print("Source packages:")

        for package in SOURCE_PACKAGES:
            print(f"  - {package}")

        print()
        print("Runtime environment variables:")

        for name in RUNTIME_ENV_VARS:
            print(f"  - {name}")

        deployment_config = {
            "source_packages": SOURCE_PACKAGES,
            "entrypoint_module": "runtime_app",
            "entrypoint_object": "app",
            "requirements_file": "requirements.txt",
            "class_methods": CLASS_METHODS,
            "display_name": "sacramento-311-agent",
            "description": (
                "Sacramento 311 AI application."
            ),
            "env_vars": RUNTIME_ENV_VARS,
            "agent_framework": "google-adk",
            "min_instances": 1,
            "max_instances": 1,
        }

        print()

        if RUNTIME_FILE.is_file():
            existing_runtime = RUNTIME_FILE.read_text(
                encoding="utf-8"
            ).strip()

            print("Updating existing 311 Agent Runtime...")
            print("Runtime:", existing_runtime)

            remote_agent = runtimes_api.update(
                name=existing_runtime,
                config=deployment_config,
            )
        else:
            print("Creating new 311 Agent Runtime...")
            remote_agent = runtimes_api.create(
                config=deployment_config
            )

    except Exception as error:
        print()
        print("=" * 78)
        print("DEPLOYMENT FAILED")
        print("=" * 78)

        print(
            f"{type(error).__name__}: {error}"
        )

        raise

    finally:
        os.chdir(original_dir)

    runtime_name = (
        remote_agent.api_resource.name
    )

    print()
    print("=" * 78)
    print("DEPLOYMENT SUCCESS")
    print("=" * 78)

    print(
        "Runtime:",
        runtime_name,
    )

    print()
    print("Supported operations:")

    print(
        remote_agent.operation_schemas()
    )

    # Record the runtime ID
    runtime_file = (
        PROJECT_DIR / "runtime_id.txt"
    )

    runtime_file.write_text(
        runtime_name + "\n",
        encoding="utf-8",
    )

    print()
    print(
        "Runtime ID recorded in:",
        runtime_file,
    )

    print()


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        print()
        print("=" * 78)
        print("FAIL")
        print("=" * 78)
        print(f"{type(error).__name__}: {error}")
        sys.exit(1)