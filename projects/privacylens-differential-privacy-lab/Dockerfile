FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .
COPY data/ ./data/
ENTRYPOINT ["privacylens"]
CMD ["data/synthetic_users.csv"]
