from typing import Any, Dict, List
import streamlit as st


def display_strengths(strengths: List[str]) -> None:
    st.markdown("""
    <div style="margin-top: 1rem; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">💪</span>
            <span style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 700; color: #0F172A;">
                Identified Strengths & High Signals
            </span>
        </div>
        <p style="color: #64748B; font-size: 0.88rem; margin-top: 2px;">
            Key parsing assets recognized favorably by automated recruitment engines
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not strengths:
        st.info("Keep refining your resume to unlock recognized parsing strengths!")
        return

    # Render items in two clean columns of glassmorphic cards
    cols = st.columns(2)
    for idx, item in enumerate(strengths):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.2);
                            border-left: 4px solid #10B981; border-radius: 12px; padding: 12px 16px;
                            margin-bottom: 10px; display: flex; align-items: flex-start; gap: 10px;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
                    <span style="color: #10B981; font-weight: 800; font-size: 1rem; line-height: 1.4;">✓</span>
                    <span style="color: #1E293B; font-size: 0.9rem; font-weight: 500; line-height: 1.5;">{item}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def display_critical_issues(analysis: Dict[str, Any]) -> None:
    critical = analysis.get("critical_issues") or []
    summary = analysis.get("issues_summary") or []

    if not critical and not summary:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25);
                        border-radius: 16px; padding: 1.25rem 1.5rem; margin-top: 1rem; display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.8rem;">🎉</span>
                <div>
                    <div style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #065F46;">
                        Zero Critical Parsing Blockers Found!
                    </div>
                    <div style="color: #047857; font-size: 0.88rem;">
                        Your resume adheres smoothly to ATS syntax, font sizing, and section header heuristics.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown("""
    <div style="margin-top: 1.25rem; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">🚨</span>
            <span style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 700; color: #0F172A;">
                High-Priority Parsing Blockers
            </span>
            <span style="background: rgba(239, 68, 68, 0.1); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.25);
                         padding: 2px 8px; border-radius: 9999px; font-size: 0.72rem; font-weight: 700;">
                IMMEDIATE ACTION
            </span>
        </div>
        <p style="color: #64748B; font-size: 0.88rem; margin-top: 2px;">
            These items directly harm automated ranking algorithms or cause parsing drops
        </p>
    </div>
    """, unsafe_allow_html=True)

    for item in critical:
        st.markdown(
            f"""
            <div style="background: rgba(239, 68, 68, 0.04); border: 1px solid rgba(239, 68, 68, 0.2);
                        border-left: 4px solid #EF4444; border-radius: 12px; padding: 12px 16px;
                        margin-bottom: 10px; display: flex; align-items: flex-start; gap: 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
                <span style="color: #EF4444; font-weight: 800; font-size: 1.1rem; line-height: 1.3;">⚠️</span>
                <span style="color: #1E293B; font-size: 0.9rem; font-weight: 500; line-height: 1.5;">{item}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    extra = [s for s in summary if s not in critical]
    if extra:
        with st.expander(f"📋 View {len(extra)} Secondary Flagged Observations", expanded=False):
            for item in extra:
                st.markdown(f"- {item}")