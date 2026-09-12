import streamlit as st
import sys
from pathlib import Path

# Put the repo root on sys.path so `from frontend.views import ...` resolves
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from frontend.services import api_client, backend_manager, supabase_client


def load_css():
    """Load custom CSS safely."""
    try:
        css_path = Path(__file__).parent / 'assets' / 'styles.css'
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f'<style>{f.read()}</style>'
    except Exception:
        pass
    return ''


def main():
    # Configure page
    try:
        st.set_page_config(
            page_title="ATS Resume Scorer",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception:
        pass

    # Auth state. Populated by Supabase sign-in / sign-up / OAuth.
    for key, default in [
        ("access_token", None),
        ("refresh_token", None),
        ("user_id", None),       # Supabase auth user id (uuid); also used by api_client
        ("user_email", None),
        ("auth_error", None),
        ("auth_info", None),
        ("current_view", "landing"),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # If we just came back from Google OAuth, exchange auth code for session
    if (
        not st.session_state.access_token
        and "code" in st.query_params
    ):
        result = supabase_client.exchange_code_for_session(st.query_params["code"])
        st.query_params.clear()
        if "error" in result:
            st.session_state.auth_error = f"Google sign-in failed: {result['error']}"
        else:
            st.session_state.access_token  = result["access_token"]
            st.session_state.refresh_token = result["refresh_token"]
            st.session_state.user_id       = result["user_id"]
            st.session_state.user_email    = result["email"]
            st.rerun()

    # Apply CSS
    st.markdown(load_css(), unsafe_allow_html=True)

    # Sync secrets to environment variables (for Streamlit Cloud deployments)
    backend_manager.sync_secrets_to_env()

    # Check backend connectivity with fast check
    backend_online = backend_manager.is_backend_online(timeout=1.5)
    if not backend_online and "backend_auto_started" not in st.session_state:
        st.session_state.backend_auto_started = True
        backend_online = backend_manager.ensure_backend_running(auto_start=True, wait_seconds=5)

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding: 6px 0 16px 0;">
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.45rem; font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
                <span>🎯 ATS SCORER</span>
                <span style="font-size: 0.65rem; font-weight: 700; background: linear-gradient(135deg, #6366F1, #D946EF); color: white; padding: 2px 8px; border-radius: 9999px; letter-spacing: 0.06em;">PRO</span>
            </div>
            <div style="color: #94A3B8; font-size: 0.78rem; margin-top: 4px;">Next-Gen Resume Optimization</div>
        </div>
        """, unsafe_allow_html=True)

        cur_view = st.session_state.current_view

        if st.button("🏠 Home Overview", use_container_width=True, key="btn_nav_home",
                     type="primary" if cur_view == "landing" else "secondary"):
            st.session_state.current_view = "landing"
            st.rerun()

        if st.button("🎯 ATS Resume Scorer", use_container_width=True, key="btn_nav_scorer",
                     type="primary" if cur_view == "scorer" else "secondary"):
            st.session_state.current_view = "scorer"
            st.rerun()

        if st.button("📝 Smart Resume Builder", use_container_width=True, key="btn_nav_builder",
                     type="primary" if cur_view == "builder" else "secondary"):
            st.session_state.current_view = "builder"
            st.rerun()

        if st.button("📊 Analysis History", use_container_width=True, key="btn_nav_history",
                     type="primary" if cur_view == "history" else "secondary"):
            st.session_state.current_view = "history"
            st.rerun()

        if st.button("📚 ATS Guide & Tips", use_container_width=True, key="btn_nav_resources",
                     type="primary" if cur_view == "resources" else "secondary"):
            st.session_state.current_view = "resources"
            st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 8px 0 16px 0;'>", unsafe_allow_html=True)

        if backend_online:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 12px; padding: 10px 14px; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div class="pulse-dot"></div>
                    <span style="color: #34D399; font-size: 0.84rem; font-weight: 600;">Neural Engine Online</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.72rem; margin-top: 4px; padding-left: 14px;">spaCy + SentenceTransformers ready</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 12px; padding: 10px 14px; margin-bottom: 8px;">
                <div style="color: #FBBF24; font-size: 0.84rem; font-weight: 600;">⚠️ Engine Offline</div>
                <div style="color: #94A3B8; font-size: 0.72rem; margin-top: 4px;">Click button below to start backend process.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Start Backend Engine", key="btn_start_backend", use_container_width=True):
                with st.spinner("Starting backend AI engine... (takes ~10s)"):
                    if backend_manager.ensure_backend_running(auto_start=True, wait_seconds=12):
                        st.success("Backend started successfully!")
                        st.rerun()
                    else:
                        st.error("Backend is still booting. Please wait a moment and click Rerun.")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.08); margin: 12px 0 16px 0;'>", unsafe_allow_html=True)
        st.markdown("### 👤 Account")

        supabase_configured = bool(supabase_client.SUPABASE_URL and supabase_client.SUPABASE_KEY)

        if st.session_state.access_token:
            st.caption(f"Signed in as **{st.session_state.user_email}**")
            if st.button("Sign out", use_container_width=True, key="btn_sign_out"):
                if supabase_configured:
                    supabase_client.sign_out()
                for k in ("access_token", "refresh_token", "user_id", "user_email"):
                    st.session_state[k] = None
                st.rerun()
        elif not supabase_configured:
            st.caption("⚡ **Guest Mode Active**")
            st.info("Full resume scoring, AI feedback, and PDF/Text downloads work locally without sign-in.")
            with st.expander("☁️ Cloud Account Setup"):
                st.caption(
                    "To enable multi-device cloud history and Supabase auth, add "
                    "`SUPABASE_URL` and `SUPABASE_KEY` to your `.env` file."
                )
        else:
            if st.session_state.auth_error:
                st.error(st.session_state.auth_error)
                st.session_state.auth_error = None
            if st.session_state.auth_info:
                st.info(st.session_state.auth_info)
                st.session_state.auth_info = None

            tab_in, tab_up = st.tabs(["Sign in", "Sign up"])

            with tab_in:
                with st.form("signin_form", clear_on_submit=False):
                    email = st.text_input("Email", key="signin_email")
                    password = st.text_input("Password", type="password", key="signin_pw")
                    submitted = st.form_submit_button("Sign in", use_container_width=True)
                if submitted:
                    result = supabase_client.sign_in_with_password(email, password)
                    if "error" in result:
                        st.session_state.auth_error = result["error"]
                    else:
                        st.session_state.access_token  = result["access_token"]
                        st.session_state.refresh_token = result["refresh_token"]
                        st.session_state.user_id       = result["user_id"]
                        st.session_state.user_email    = result["email"]
                    st.rerun()

            with tab_up:
                with st.form("signup_form", clear_on_submit=False):
                    email_up = st.text_input("Email", key="signup_email")
                    password_up = st.text_input("Password (min 6 chars)", type="password", key="signup_pw")
                    submitted_up = st.form_submit_button("Create account", use_container_width=True)
                if submitted_up:
                    result = supabase_client.sign_up_with_password(email_up, password_up)
                    if "error" in result:
                        st.session_state.auth_error = result["error"]
                    elif result.get("pending_confirmation"):
                        st.session_state.auth_info = (
                            f"Check your inbox — confirmation email sent to {result['email']}."
                        )
                    else:
                        st.session_state.access_token  = result["access_token"]
                        st.session_state.refresh_token = result["refresh_token"]
                        st.session_state.user_id       = result["user_id"]
                        st.session_state.user_email    = result["email"]
                    st.rerun()

            oauth = supabase_client.google_oauth_url()
            if "url" in oauth:
                st.markdown("<div style='text-align:center; margin: 8px 0; color:#94a3b8;'>or</div>",
                            unsafe_allow_html=True)
                st.link_button(
                    "Continue with Google",
                    url=oauth["url"],
                    use_container_width=True,
                )

    # Main content area - render based on current view
    cur_view = st.session_state.current_view
    if cur_view == 'landing':
        from frontend.views import landing
        landing.render()
    elif cur_view == 'scorer':
        from frontend.views import scorer
        scorer.render()
    elif cur_view == 'builder':
        from frontend.views import builder
        builder.render()
    elif cur_view == 'history':
        from frontend.views import history
        history.render()
    elif cur_view == 'resources':
        from frontend.views import resources
        resources.render()
    else:
        st.session_state.current_view = 'landing'
        from frontend.views import landing
        landing.render()


if __name__ == "__main__":
    main()