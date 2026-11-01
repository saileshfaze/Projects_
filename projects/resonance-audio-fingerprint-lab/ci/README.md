# CI template

The workflow in `project-ci.yml` is intentionally nested in the project folder to avoid modifying unrelated repository-wide automation. GitHub Actions does not execute nested workflow templates. To activate, copy it to the repository root `.github/workflows/resonance-ci.yml` and review its permissions, dependency pins, and triggers.
