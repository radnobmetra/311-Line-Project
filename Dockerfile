# syntax=docker/dockerfile:1

###############################################################################
# 311 Line Project - City of Sacramento 311 SMS line
#
# The image contains every runtime dependency of the project:
#   * Google ADK / Gemini multi-agent system   -> my_agent/, modelarmor_agent/
#   * Flask + Twilio SMS webhook               -> reply_sms.py (port 3000)
#   * Elasticsearch + Vertex AI ranking (RAG)  -> my_agent/subagents/tools/
#   * Geo stack (GeoPandas / Shapely / GeoPy)  -> city limits verification
#
# Python 3.14 is used so the code runs on the newest interpreter the team
# targets (PEP 701 f-strings, PEP 695 generics, free-threading capable builds).
#
# Build:  docker build -t 311-line-project .
# Run:    docker run --rm -p 3000:3000 --env-file .env 311-line-project
###############################################################################
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=3000

# Base image only ships the Python runtime; tzdata is needed by
# zoneinfo.ZoneInfo("America/Los_Angeles") in the ticket lookup tool.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies are installed in their own layer so source changes do not
# invalidate the (slow) pip install layer.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code, agent definitions, knowledge/index data and bundled files.
COPY . .

# Run as a non-root user. Two locations have to stay writable:
#   * /app             -> session state written next to the code
#                         (useronline.json, sessions.log, .adk/)
#   * site-packages    -> the ADK dev UI (`adk web`) rewrites its browser
#                         runtime-config.json inside the installed package,
#                         otherwise it logs "[Errno 13] Permission denied"
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/.adk \
    && chown -R appuser:appuser /app \
    && SITE_PACKAGES="$(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")" \
    && mkdir -p "$SITE_PACKAGES/google/adk/cli/browser/assets/config" \
    && chown -R appuser:appuser "$SITE_PACKAGES/google/adk/cli/browser/assets"
USER appuser

# 3000 = Twilio SMS webhook (gunicorn), 8000 = ADK dev UI / web playground
EXPOSE 3000 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import socket, sys; s = socket.socket(); s.settimeout(3); sys.exit(0 if s.connect_ex(('127.0.0.1', 3000)) == 0 else 1)"]

# A single worker keeps one inactivity-timer thread (started on `import my_agent`),
# threads allow the webhook to handle concurrent texts.
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "1", "--threads", "4", "--timeout", "300", "--access-logfile", "-", "reply_sms:app"]
