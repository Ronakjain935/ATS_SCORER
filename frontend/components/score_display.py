from typing import Any, Dict

import streamlit as st

from frontend.components._helpers import get_score_color, get_score_emoji, get_score_status


# Component max scores match backend/core/config.py SCORE_WEIGHTS.
# (Backend returns each component's score on its own scale, not 0–100.)
COMPONENTS = [
    ("Formatting",        "formatting",        20, "📝", "#6366F1"),
    ("Keywords & Skills", "keywords",          25, "🔑", "#06B6D4"),
    ("Content Quality",   "content",           25, "📄", "#8B5CF6"),
    ("Skill Validation",  "skill_validation",  15, "✅", "#10B981"),
    ("ATS Compatibility", "ats_compatibility", 15, "🤖", "#EC4899"),
]


def display_overall_score(analysis: Dict[str, Any]) -> None:
    """Big glowing score card with status pills and modern typography."""
    score = float(analysis.get("ATS_score", analysis.get("ats_score", 0)))
    interpretation = analysis.get("interpretation", "Audit completed successfully.")
    text_color, bg_color, border_color = get_score_color(score)
    emoji = get_score_emoji(score)
    status_text = get_score_status(score)

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <div class="hero-badge"><span class="pulse-dot"></span> AUDIT SYNTHESIS</div>
        <h2 class="gradient-text" style="font-size: 2.2rem; margin-bottom: 0.25rem;">Neural ATS Evaluation</h2>
        <p style="color: #64748B; font-size: 0.95rem;">Multi-dimensional algorithmic breakdown across 5 weighted parsing pillars</p>
    </div>
    """, unsafe_allow_html=True)

    c_score, c_info = st.columns([1.2, 2])

    with c_score:
        st.markdown(
            f"""
            <div style="background: {bg_color}; border: 1.5px solid {border_color};
                        border-radius: 20px; padding: 2rem 1.5rem; text-align: center;
                        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.06); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -40px; right: -40px; width: 100px; height: 100px;
                            background: radial-gradient(circle, {text_color}22 0%, transparent 70%); border-radius: 50%;"></div>
                <div style="display: inline-block; background: {text_color}18; color: {text_color};
                            padding: 4px 12px; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;
                            letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                    {status_text}
                </div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 4.5rem; font-weight: 800;
                            color: {text_color}; line-height: 1; margin: 0.25rem 0;">
                    {score:.0f}<span style="font-size: 1.8rem; color: #94A3B8; font-weight: 500;">/100</span>
                </div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: #0F172A; margin-top: 0.5rem;">
                    Overall ATS Match Index
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_info:
        st.markdown(
            f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 20px;
                        padding: 1.75rem 1.5rem; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
                        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
                        <span style="font-size: 1.25rem;">{emoji}</span>
                        <span style="font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #0F172A;">
                            Executive Parsing Summary
                        </span>
                    </div>
                    <p style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.25rem;">
                        {interpretation}
                    </p>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #F8FAFC; padding: 12px; border-radius: 12px;">
                    <div>
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Parser Readability</div>
                        <div style="font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: #0F172A;">
                            {'High (Machine-Ready)' if score >= 75 else 'Moderate' if score >= 55 else 'At Risk'}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Estimated Pass Rate</div>
                        <div style="font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: {text_color};">
                            {'Top 10% • 95% Pass' if score >= 85 else 'Top 25% • 80% Pass' if score >= 70 else 'Average • 50% Pass' if score >= 50 else 'Bottom Tier • <25%'}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_score_breakdown(analysis: Dict[str, Any]) -> None:
    """Five elevated progress cards, one per scoring component."""
    component_scores = analysis.get("component_scores") or {}
    st.markdown("""
    <div style="margin-top: 1.5rem; margin-bottom: 1rem;">
        <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 700; color: #0F172A; margin-bottom: 0.25rem;">
            📈 Weighted Component Breakdown
        </h3>
        <p style="color: #64748B; font-size: 0.88rem;">Each pillar is calibrated against top Applicant Tracking Systems standards</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2)
    for i, (label, key, max_score, icon, accent_col) in enumerate(COMPONENTS):
        value = float(component_scores.get(key, 0))
        percentage = min(max(value / max_score, 0.0), 1.0) if max_score else 0
        pct_display = int(percentage * 100)

        with left if i % 2 == 0 else right:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
                            padding: 1rem 1.25rem; margin-bottom: 0.85rem; box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.1rem;">{icon}</span>
                            <span style="font-weight: 700; font-size: 0.92rem; color: #1E293B;">{label}</span>
                        </div>
                        <div style="display: flex; align-items: baseline; gap: 4px;">
                            <span style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.1rem; color: #0F172A;">{value:.0f}</span>
                            <span style="font-size: 0.78rem; color: #94A3B8; font-weight: 600;">/{max_score}</span>
                            <span style="background: {accent_col}15; color: {accent_col}; padding: 2px 6px; border-radius: 6px; font-size: 0.72rem; font-weight: 700; margin-left: 6px;">
                                {pct_display}%
                            </span>
                        </div>
                    </div>
                    <div style="background-color: #F1F5F9; border-radius: 9999px; height: 8px; overflow: hidden; width: 100%;">
                        <div style="background: linear-gradient(90deg, {accent_col}, {accent_col}DD); width: {percentage * 100}%;
                                    height: 100%; border-radius: 9999px; transition: width 0.6s ease;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )