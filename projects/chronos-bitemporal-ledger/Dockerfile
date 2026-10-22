FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CHRONOS_DB=/data/chronos.sqlite3
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN mkdir -p /data && useradd --system --uid 10001 chronos && chown chronos:chronos /data
USER chronos
EXPOSE 8000
CMD ["uvicorn", "chronos_ledger.api:app", "--host", "0.0.0.0", "--port", "8000"]
