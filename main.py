import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    import streamlit as st
    is_streamlit = st.runtime.exists()
except Exception:
    is_streamlit = False

if is_streamlit:
    try:
        import frontend.app
    except ImportError:
        import frontend.streamlite_app
elif __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("[ATS Scorer] Starting Backend on http://localhost:8000")
    print("[ATS Scorer] API Documentation: http://localhost:8000/docs")
    print("[ATS Scorer] To launch the Streamlit frontend, run:")
    print("   streamlit run frontend/app.py")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
