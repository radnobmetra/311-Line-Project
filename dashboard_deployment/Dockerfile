# Build Angular.
FROM node:24-bookworm-slim AS frontend-build

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY frontend/ ./

RUN npm run build -- --configuration production --output-path=dist/dashboard


# Run Flask and serve the Angular build.
FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

COPY --from=frontend-build /frontend/dist/dashboard/browser/ ./static/

RUN useradd --create-home appuser
USER appuser

EXPOSE 8080

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 --timeout 120 --access-logfile - --error-logfile - backend.app:app"]