import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv

    # Load root .env or backend/.env if available
    root_dir = Path(__file__).resolve().parent.parent.parent
    load_dotenv(root_dir / ".env")
    load_dotenv(root_dir / "backend" / ".env")
except ImportError:
    pass

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
AUTH_REDIRECTED_URL = os.getenv("AUTH_REDIRECTED_URL", "http://localhost:8501")

_client: Optional[Any] = None


def get_client() -> Optional[Any]:
    global _client
    if _client is None and create_client and SUPABASE_URL and SUPABASE_KEY:
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception:
            _client = None
    return _client


def sign_in_with_password(email: str, password: str) -> Dict[str, Any]:
    client = get_client()
    if not client:
        return {"error": "Supabase client not initialized. Check your SUPABASE_URL and SUPABASE_KEY."}

    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res and res.session:
            return {
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token,
                "user_id": res.user.id if res.user else None,
                "email": res.user.email if res.user else email,
            }
        return {"error": "Invalid login response from server."}
    except Exception as exc:
        # Extract user-friendly error message if available
        msg = str(exc)
        if hasattr(exc, "message"):
            msg = exc.message
        return {"error": msg}


def sign_up_with_password(email: str, password: str) -> Dict[str, Any]:
    client = get_client()
    if not client:
        return {"error": "Supabase client not initialized. Check your SUPABASE_URL and SUPABASE_KEY."}

    try:
        res = client.auth.sign_up({"email": email, "password": password})
        if res and res.session:
            return {
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token,
                "user_id": res.user.id if res.user else None,
                "email": res.user.email if res.user else email,
            }
        # If email confirmation is required, session is None but user is created
        return {
            "pending_confirmation": True,
            "email": email,
        }
    except Exception as exc:
        msg = str(exc)
        if hasattr(exc, "message"):
            msg = exc.message
        return {"error": msg}


def sign_out() -> None:
    client = get_client()
    if client:
        try:
            client.auth.sign_out()
        except Exception:
            pass


def exchange_code_for_session(code: str) -> Dict[str, Any]:
    client = get_client()
    if not client:
        return {"error": "Supabase client not initialized."}

    try:
        res = client.auth.exchange_code_for_session({"auth_code": code})
        if res and res.session:
            return {
                "access_token": res.session.access_token,
                "refresh_token": res.session.refresh_token,
                "user_id": res.user.id if res.user else None,
                "email": res.user.email if res.user else None,
            }
        return {"error": "Failed to exchange auth code for session."}
    except Exception as exc:
        return {"error": str(exc)}


_google_enabled: Optional[bool] = None


def is_google_provider_enabled() -> bool:
    global _google_enabled
    if _google_enabled is not None:
        return _google_enabled
    if not SUPABASE_URL or not SUPABASE_KEY:
        _google_enabled = False
        return False
    try:
        import httpx
        url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/settings"
        resp = httpx.get(url, headers={"apikey": SUPABASE_KEY}, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            _google_enabled = bool(data.get("external", {}).get("google", False))
            return _google_enabled
    except Exception:
        pass
    _google_enabled = False
    return False


def google_oauth_url() -> Dict[str, Any]:
    client = get_client()
    if not client:
        return {"error": "Supabase client not initialized."}

    if not is_google_provider_enabled():
        return {
            "error": "Google Sign-In is not enabled in your Supabase project. Please use Email/Password login above, or enable Google in the Supabase Dashboard (Authentication -> Providers -> Google)."
        }

    try:
        res = client.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": AUTH_REDIRECTED_URL,
            }
        })
        if hasattr(res, "url") and res.url:
            return {"url": res.url}
        elif isinstance(res, dict) and "url" in res:
            return {"url": res["url"]}
        return {"error": "OAuth redirect URL could not be generated."}
    except Exception as exc:
        err_msg = str(exc)
        if "Unsupported provider" in err_msg or "provider is not enabled" in err_msg:
            err_msg = "Google sign-in is not enabled in your Supabase project (Authentication -> Providers -> Google)."
        return {"error": err_msg}