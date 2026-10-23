# API contracts

`POST /v1/documents`: `{"documents":[{"id":"a","title":"Policy","body":"...","source":"synthetic","category":"ops"}]}`. Upserts the batch transactionally.

`POST /v1/search`: `{"query":"cache expiry","k":5}`. Returns `hits` with document IDs, scores, source/category, and component ranks.

`POST /v1/answer`: same request as search. Returns `answer`, `abstained`, `citations` (`document_id`, `start`, `end`, `excerpt`, `query_term_overlap`), and `filtered_documents`.

`POST /v1/evaluate`: `{"questions":[{"id":"q1","question":"cache expiry","slice":"ops"}],"qrels":{"q1":["a"]},"k":5}`. Returns overall, per-query, per-slice metrics, bootstrap intervals and persisted `evaluation_id`.

`GET /health`: returns `{"status":"ok"}`. Validation errors use HTTP 422. No API auth is implemented; localhost use only.
