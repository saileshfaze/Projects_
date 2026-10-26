FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir '.[api]'
RUN useradd --system --uid 10001 appuser && mkdir -p /data && chown appuser /data
USER appuser
ENV CHAINSENTRY_DB=/data/chainsentry.db
EXPOSE 8000
CMD ["uvicorn", "chainsentry.api:app", "--host", "0.0.0.0", "--port", "8000"]
