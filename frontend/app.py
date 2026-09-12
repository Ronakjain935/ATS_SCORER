import sys
from pathlib import Path

# Ensure repository root is on sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Ensure secrets are synced to environment variables for cloud deployments
try:
    from frontend.services.backend_manager import sync_secrets_to_env
    sync_secrets_to_env()
except Exception:
    pass

# Import and execute the main Streamlit application
from frontend.streamlite_app import main

main()
