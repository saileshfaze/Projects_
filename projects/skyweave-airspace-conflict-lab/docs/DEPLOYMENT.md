# Local deployment

Development: `uvicorn skyweave.api:app --host 127.0.0.1 --port 8000`.
Container: `docker compose up --build`, then visit `http://127.0.0.1:8080/docs`.
The Compose service uses an ephemeral SQLite database and binds only to loopback.
Do not expose the application to public networks without authentication, rate limits,
logging, TLS, and a security review. This project is not an aviation operations tool.
