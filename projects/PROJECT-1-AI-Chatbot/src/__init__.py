from pathlib import Path

from flask import Flask

from .views import register_routes


def create_app():
    # Point the Flask app to the repository-level `templates/` directory
    repo_root = Path(__file__).parent.parent
    templates_dir = str(repo_root / "templates")

    app = Flask(__name__, template_folder=templates_dir)
    register_routes(app)
    return app


# Convenience export used by the top-level launcher
app = create_app()
