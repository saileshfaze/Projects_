FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --create-home --uid 10001 app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir '.[api]' && mkdir -p /app/var && chown -R app:app /app/var
USER app
ENV CAUSALPILOT_DB=/app/var/causalpilot.sqlite3
EXPOSE 8000
CMD ["uvicorn", "causalpilot.api:app", "--host", "0.0.0.0", "--port", "8000"]
