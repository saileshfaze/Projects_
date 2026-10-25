FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 terraflux
RUN mkdir -p /app/data/generated /app/state && chown -R terraflux:terraflux /app
USER terraflux
EXPOSE 8000
CMD ["uvicorn", "terraflux.api:app", "--host", "0.0.0.0", "--port", "8000"]
