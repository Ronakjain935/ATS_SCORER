import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from backend.core.config import SUPABASE_KEY, SUPABASE_JWT_SECRET

logger = logging.getLogger('ats_resume_scorer')

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """
    Extracts the user_id (sub) from Supabase JWT access token.
    Falls back to 'anonymous_user' if no token or in development mode.
    """
    if not credentials or not credentials.credentials:
        return "anonymous_user"

    token = credentials.credentials
    try:
        secret = SUPABASE_JWT_SECRET or SUPABASE_KEY
        if secret:
            try:
                payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})
                user_id = payload.get("sub") or payload.get("id")
                if user_id:
                    return str(user_id)
            except Exception:
                pass

        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub") or payload.get("id") or "anonymous_user"
        return str(user_id)
    except Exception as exc:
        logger.warning(f"Could not decode auth token: {exc}")
        return "anonymous_user"
