FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY data ./data
ENTRYPOINT ["hydrograph"]
CMD ["--network", "data/network.json", "--output", "artifacts/report.json", "--svg", "artifacts/network.svg"]
