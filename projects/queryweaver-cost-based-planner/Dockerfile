FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir '.[api]'
RUN useradd --system --uid 10001 queryweaver
USER queryweaver
EXPOSE 8000
CMD ["uvicorn", "queryweaver.api:app", "--host", "0.0.0.0", "--port", "8000"]
