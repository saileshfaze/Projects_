import os
from .api import create_app
app = create_app(os.environ.get("VAULTLINE_DIR", "/data/vault"))
