# Architecture

AutoFlow Intelligence is intentionally built in a simple, recruiter-friendly full-stack structure.

## Frontend

- `index.php` renders the application shell.
- `assets/css/styles.css` contains the complete responsive visual system.
- `assets/js/app.js` consumes REST-style PHP endpoints and renders dashboards, inventory cards, lead rows, charts, and assistant output.

## Backend

- `api/bootstrap.php` handles JSON headers, shared helpers, and data loading.
- `api/overview.php` aggregates KPIs and target progress.
- `api/inventory.php` exposes searchable and filterable vehicle data.
- `api/leads.php` exposes CRM pipeline data.
- `api/assistant.php` creates AI-style recommendations from business signals.

## Data Layer

The local demo reads from JSON seed files so the project runs immediately. A production-style MySQL schema is included in `database/schema.sql`.

## Why This Project Fits The Resume

This project connects web development, API integration, data analysis, e-commerce operations, and AI automation. It reflects experience with PHP, MySQL, HTML, CSS, JavaScript, REST APIs, GitHub-ready documentation, and business-facing dashboard design.

