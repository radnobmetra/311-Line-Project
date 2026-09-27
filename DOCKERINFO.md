## Docker

The repository ships a [`Dockerfile`](Dockerfile) containing every runtime dependency for the
311 SMS line (Google ADK / Gemini agents, the Flask + Twilio webhook, the Elasticsearch +
Vertex AI ranking tools and the GeoPandas/Shapely address tooling).

Build the image:

```bash
docker build -t 311-line-project .
```

Run it (the `.env` file provides the `GOOGLE_*`, `ELASTIC_*` and `TWILIO_*` values):

```bash
docker run --rm -p 3000:3000 --env-file .env 311-line-project
```

`sa-key.json` is a secret and is deliberately excluded from the image via `.dockerignore`.
Mount it when the container needs Google Cloud credentials:

```bash
docker run --rm -p 3000:3000 --env-file .env \
  -v "$PWD/sa-key.json:/secrets/sa-key.json:ro" \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/sa-key.json \
  311-line-project
```

Or use Compose, which already wires up the `.env` file and the service-account key:

```bash
docker compose up --build
```

The Twilio webhook is served by Gunicorn on port `3000` at `POST /reply_sms`, so point the
Twilio phone number's "A message comes in" webhook at `https://<host>/reply_sms`.

Verify the container:

```bash
curl -X POST http://localhost:3000/reply_sms -d "From=%2B15551234567&Body=hello"
docker inspect --format "{{.State.Health.Status}}" 311-line-api   # healthcheck
```

### Running the ADK CLI (`adk`) inside the container

The image installs the Google ADK CLI (`google-adk`), so the agents can be driven exactly like
on a dev machine. The container's default command is the Gunicorn webhook, so start the CLI
yourself — `docker exec` starts in `/app`, which is where `my_agent/` lives:

```bash
# Interactive CLI for the agent  (the -it matters: adk run needs a TTY)
docker exec -it 311-line-api adk run my_agent

# Version / available commands
docker exec 311-line-api adk --version
docker exec 311-line-api adk --help
```

Both CLIs read their configuration from the container's environment, so they only reach Gemini
when the container was started with the project's credentials (`GOOGLE_CLOUD_PROJECT`,
`GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_APPLICATION_CREDENTIALS` + the mounted `sa-key.json`) —
without them you get `ValueError: No API key was provided`.

The **web UI needs two extra things in Docker**:

1. `adk web` binds `127.0.0.1` by default, which is *not* reachable through a published port,
   so it must be told to bind all interfaces: `--host 0.0.0.0`.
2. Port `8000` has to be published **when the container is created** — Docker cannot publish a
   port on an already running container.

The easiest way is the `dev` profile in Compose, which does both for you:

```bash
docker compose --profile dev up -d adk-web   # -> http://localhost:8000
docker compose --profile dev stop adk-web    # stop only the dev UI (not the api service)
```


If you are exec-ing into a container that was started **without** `-p 8000:8000`, the server will
run but the UI will not be reachable from the host; recreate the container (Compose above) or use
`adk run` for CLI-only testing.

#### Notes

- The image is based on `python:3.14-slim`, so the container always runs the project's
  target interpreter (Python 3.14).
- The image makes the ADK package's browser assets writable by the `appuser` user, because
  `adk web` rewrites `.../google/adk/cli/browser/assets/config/runtime-config.json` inside
  site-packages on startup and otherwise logs `[Errno 13] Permission denied`.
  Containers created from an older build can be fixed without rebuilding by running:
  `docker exec -u root <container> chown -R appuser:appuser /usr/local/lib/python3.14/site-packages/google/adk/cli/browser/assets`
- Dependencies live in [`requirements.txt`](requirements.txt); rebuild the image after changing it.
- The inactivity timer (`timerloop.py`) is a background thread started on `import my_agent`,
  so the image intentionally runs a **single** Gunicorn worker (with threads) to avoid
  multiple competing timers.
- `sessions.log`, `useronline.json` and `.adk/` are runtime state that the app creates on
  first write; they are not baked into the image.
- GitHub Actions builds and pushes this image on every push to `main` via
  [`.github/workflows/docker-ci.yml`](.github/workflows/docker-ci.yml).