import os
from typing import Any, Dict, List, Optional
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")


def _auth_headers(access_token: Optional[str] = None) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def analyze_resume(
    resume_file: Any,
    access_token: Optional[str] = None,
    job_description: str = "",
) -> Dict[str, Any]:
    """
    Sends resume file and optional JD to the backend for ATS scoring.
    """
    url = f"{BACKEND_URL}/api/v1/analyze-resume"
    headers = _auth_headers(access_token)

    # Read bytes and file name from Streamlit UploadedFile or file-like object
    if hasattr(resume_file, "name"):
        filename = resume_file.name
    else:
        filename = "resume.pdf"

    if hasattr(resume_file, "getvalue"):
        content = resume_file.getvalue()
    elif hasattr(resume_file, "read"):
        content = resume_file.read()
    else:
        content = bytes(resume_file)

    mime_type = getattr(resume_file, "type", None) or "application/octet-stream"

    files = {
        "resume": (filename, content, mime_type),
    }
    data = {
        "job_description": job_description or "",
    }

    response = requests.post(url, files=files, data=data, headers=headers, timeout=120)
    response.raise_for_status()
    return response.json()


def generate_pdf(
    analysis: Dict[str, Any],
    access_token: Optional[str] = None,
) -> bytes:
    """
    Sends analysis result to backend to generate a combined PDF report.
    """
    url = f"{BACKEND_URL}/api/v1/generate-pdf"
    headers = _auth_headers(access_token)
    headers["Content-Type"] = "application/json"

    response = requests.post(url, json=analysis, headers=headers, timeout=60)
    response.raise_for_status()
    return response.content


def get_history(access_token: str) -> List[Dict[str, Any]]:
    """
    Retrieves the past analyses for the authenticated user.
    """
    url = f"{BACKEND_URL}/api/v1/history"
    headers = _auth_headers(access_token)

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def delete_history_entry(analysis_id: str, access_token: str) -> Dict[str, Any]:
    """
    Deletes an analysis record from history.
    """
    url = f"{BACKEND_URL}/api/v1/history/{analysis_id}"
    headers = _auth_headers(access_token)

    response = requests.delete(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def get_history_pdf(analysis_id: str, access_token: str) -> bytes:
    """
    Downloads historical analysis PDF by ID.
    """
    url = f"{BACKEND_URL}/api/v1/history/{analysis_id}/pdf"
    headers = _auth_headers(access_token)

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.content


def check_health() -> Dict[str, Any]:
    """
    Checks backend health and model readiness.
    """
    bases = [BACKEND_URL]
    if "127.0.0.1" not in BACKEND_URL:
        bases.append("http://127.0.0.1:8000")
    if "localhost" not in BACKEND_URL:
        bases.append("http://localhost:8000")

    for base in bases:
        for path in ["/api/v1/health", "/health"]:
            try:
                response = requests.get(f"{base}{path}", timeout=3)
                if response.status_code == 200:
                    return response.json()
            except Exception:
                continue

    raise requests.exceptions.ConnectionError("Could not reach backend health endpoint")