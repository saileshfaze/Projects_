FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AEGIS_DB_PATH=/var/lib/aegis/features.db

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && \
    mkdir -p /var/lib/aegis && \
    chown -R 65532:65532 /var/lib/aegis
USER 65532:65532
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/ready', timeout=2)"
CMD ["uvicorn", "aegis_feature_store.api:app", "--host", "0.0.0.0", "--port", "8000"]
