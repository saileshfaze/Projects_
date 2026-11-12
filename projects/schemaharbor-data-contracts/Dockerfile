FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY data ./data
ENTRYPOINT ["schemaharbor"]
CMD ["diff", "data/orders-v1.json", "data/orders-v2.json"]
