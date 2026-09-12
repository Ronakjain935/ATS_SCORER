import requests
import streamlit as st

from frontend.services import api_client


def _show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Is it running on port 8000?")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        st.error(f"Backend returned {exc.response.status_code}: {exc.response.text}")
    else:
        st.error(f"Unexpected error: {exc}")


def render() -> None:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <div class="hero-badge"><span class="pulse-dot"></span> AUDIT ARCHIVE</div>
        <h1 class="gradient-text" style="font-size: 2.6rem; margin-bottom: 0.5rem;">Analysis & Score History</h1>
        <p style="color: #475569; font-size: 1.05rem; max-width: 820px; line-height: 1.6;">
            Review past parsing audits, monitor score trajectory over revisions, and compare ATS match benchmarks.
        </p>
    </div>
    """, unsafe_allow_html=True)

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.2);
                    border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <div style="font-weight: 700; font-size: 1rem; color: #1E293B; margin-bottom: 4px;">
                ☁️ Cloud History Sync
            </div>
            <div style="color: #64748B; font-size: 0.9rem;">
                Sign in from the left sidebar using your email or Google account to automatically preserve and sync all historical ATS audits permanently across devices.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("scorer_analysis"):
            recent = st.session_state["scorer_analysis"]
            score = float(recent.get("ATS_score", recent.get("ats_score", 0)))
            score_col = "#10B981" if score >= 80 else "#F59E0B" if score >= 60 else "#EF4444"

            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(15,23,42,0.04); margin-bottom: 1rem;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Most Recent Session Scan</div>
                <div style="display: flex; align-items: baseline; gap: 8px; margin: 6px 0 12px 0;">
                    <span style="font-family: 'Outfit', sans-serif; font-size: 2.5rem; font-weight: 800; color: {score_col};">{score:.0f}</span>
                    <span style="font-size: 1rem; color: #94A3B8; font-weight: 600;">/100 ATS Score</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🎯 Open Full Results in ATS Scorer", key="btn_history_view_recent", type="primary"):
                st.session_state.current_view = "scorer"
                st.rerun()
        else:
            st.markdown("""
            <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 16px; padding: 2.5rem; text-align: center; margin-top: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.15rem; color: #0F172A;">No Audits in Current Session</div>
                <p style="color: #64748B; font-size: 0.9rem; margin: 0.5rem auto 1.25rem auto; max-width: 450px;">
                    Upload your resume or craft one in Resume Studio to see a comprehensive multi-pillar breakdown.
                </p>
            </div>
            """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 1.5, 1])
            with col2:
                if st.button("🚀 Analyze a Resume Now", key="btn_history_start_scorer", type="primary", use_container_width=True):
                    st.session_state.current_view = "scorer"
                    st.rerun()
        return

    try:
        history = api_client.get_history(access_token)
    except requests.RequestException as exc:
        _show_backend_error(exc)
        return

    if not history:
        st.markdown("""
        <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 16px; padding: 2.5rem; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.15rem; color: #0F172A;">No Saved Audits Yet</div>
            <p style="color: #64748B; font-size: 0.9rem; margin: 0.5rem auto 1.25rem auto; max-width: 450px;">
                Your account is ready! Run your first resume scan to populate this timeline.
            </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            if st.button("🎯 Go to ATS Scorer", key="btn_history_go_scorer", type="primary", use_container_width=True):
                st.session_state.current_view = "scorer"
                st.rerun()
        return

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <span style="font-weight: 700; color: #0F172A; font-size: 1rem;">Archived Audits ({len(history)})</span>
        <span style="background: rgba(16, 185, 129, 0.1); color: #10B981; padding: 2px 10px; border-radius: 9999px; font-size: 0.78rem; font-weight: 700;">
            Cloud Synced
        </span>
    </div>
    """, unsafe_allow_html=True)

    for idx, entry in enumerate(history):
        filename = entry.get("filename", "resume")
        ats_score = float(entry.get("ats_score", 0))
        created_at = entry.get("created_at", "")[:10]
        analysis = entry.get("analysis_result", {}) or {}
        score_col = "#10B981" if ats_score >= 80 else "#F59E0B" if ats_score >= 60 else "#EF4444"

        component_scores = analysis.get("component_scores", {}) or {}
        jd_comparison = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")

        with st.expander(f"📄 {filename} — Score: {ats_score:.0f}/100 ({created_at})"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Overall Score", f"{ats_score:.0f}/100")
                st.metric("Formatting", f"{component_scores.get('formatting', 0):.0f}/20")
            with c2:
                st.metric("Keywords", f"{component_scores.get('keywords', 0):.0f}/25")
                st.metric("Content", f"{component_scores.get('content', 0):.0f}/25")
            with c3:
                st.metric("Skill Validation", f"{component_scores.get('skill_validation', 0):.0f}/15")
                st.metric("ATS Compatibility", f"{component_scores.get('ats_compatibility', 0):.0f}/15")

            if jd_comparison:
                st.markdown(f"**Target JD Match:** `{jd_comparison.get('match_percentage', 0):.0f}%`")

            entry_id = entry.get("id")
            if entry_id:
                if st.button("🗑️ Remove Entry", key=f"delete_{idx}"):
                    try:
                        api_client.delete_history_entry(str(entry_id), access_token)
                        st.success("Entry removed from history.")
                        st.rerun()
                    except requests.RequestException as exc:
                        _show_backend_error(exc)