# Atlas CRE Desk

Atlas CRE Desk is a professional full-stack demo app for commercial real estate teams managing acquisitions, underwriting, diligence, and investment committee readiness.

It is intentionally dependency-free: the backend uses Node.js core modules, the front end uses modern HTML/CSS/JavaScript, and tests use Node's built-in test runner.

## Features

- Secure signed session cookies with constant-time verification
- REST API for portfolio KPIs, deal pipeline, diligence tasks, and activity
- JSON-backed persistence with atomic writes
- Executive dashboard with pipeline filters, task updates, and audit activity
- Seed data for realistic CRE workflows
- Built-in validation, centralized responses, and focused tests

## Run

```bash
npm test
npm run dev
```

Then open:

```text
http://localhost:4173
```

Demo login:

```text
Email: analyst@atlas.local
Password: demo-password
```

## API

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/session`
- `GET /api/dashboard`
- `GET /api/deals`
- `POST /api/deals`
- `PATCH /api/deals/:id`
- `PATCH /api/tasks/:id`

## Structure

```text
src/server.mjs       HTTP server, router, API controllers
src/data/store.mjs   JSON persistence and domain operations
src/security/auth.mjs signed session helpers
public/              front-end application
tests/               Node test suite
```
