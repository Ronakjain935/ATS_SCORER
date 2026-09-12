from typing import Any, Dict, Optional

import streamlit as st


def display_jd_comparison(jd_comparison: Optional[Dict[str, Any]]) -> None:
    if not jd_comparison:
        return  # caller decides whether to render the section at all

    match_pct = float(jd_comparison.get("match_percentage", 0))
    semantic = float(jd_comparison.get("semantic_similarity", 0))
    matched = jd_comparison.get("matched_keywords", []) or []
    missing = jd_comparison.get("missing_keywords", []) or []
    gap = jd_comparison.get("skills_gap", []) or []

    st.markdown("""
    <div style="margin-top: 1.25rem; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">🎯</span>
            <span style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 700; color: #0F172A;">
                Target Job Description Alignment
            </span>
        </div>
        <p style="color: #64748B; font-size: 0.88rem; margin-top: 2px;">
            NLP lexical overlap and bi-encoder semantic proximity against your posted vacancy
        </p>
    </div>
    """, unsafe_allow_html=True)

    top_l, top_r = st.columns(2)
    with top_l:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 14px; text-align: center;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Keyword Overlap</div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; color: #6366F1;">{match_pct:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 14px; text-align: center;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Semantic Closeness</div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; color: #8B5CF6;">{semantic * 100:.0f}%</div>
            </div>
            """, unsafe_allow_html=True)

    with top_r:
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.04); border: 1px solid rgba(99, 102, 241, 0.15); border-radius: 14px; padding: 14px 18px; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-weight: 700; font-size: 0.9rem; color: #1E293B; margin-bottom: 4px;">Matching Diagnosis</div>
            <div style="color: #475569; font-size: 0.85rem; line-height: 1.5;">
                {'Strong alignment. Your vocabulary mirrors key job competencies accurately.' if match_pct >= 70 else 'Moderate gap detected. Integrating missing core terms will significantly boost ATS screening velocity.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    bot_l, bot_r = st.columns(2)
    with bot_l:
        st.markdown("""
        <div style="font-weight: 700; font-size: 0.92rem; color: #065F46; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            <span>✅</span> <span>Matched Keywords In Resume</span>
        </div>
        """, unsafe_allow_html=True)
        if matched:
            pills = " ".join(
                f"<span style='display:inline-block; background:rgba(16,185,129,0.08); color:#059669; border:1px solid rgba(16,185,129,0.25); border-radius:9999px; padding:4px 11px; font-size:0.8rem; font-weight:600; margin:3px;'>✓ {kw}</span>"
                for kw in matched[:18]
            )
            st.markdown(f"<div style='margin-bottom: 12px;'>{pills}</div>", unsafe_allow_html=True)
        else:
            st.info("No direct keyword matches found yet.")

    with bot_r:
        st.markdown("""
        <div style="font-weight: 700; font-size: 0.92rem; color: #991B1B; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            <span>❌</span> <span>Missing Job Description Keywords</span>
        </div>
        """, unsafe_allow_html=True)
        if missing:
            pills = " ".join(
                f"<span style='display:inline-block; background:rgba(239,68,68,0.08); color:#DC2626; border:1px solid rgba(239,68,68,0.25); border-radius:9999px; padding:4px 11px; font-size:0.8rem; font-weight:600; margin:3px;'>+ {kw}</span>"
                for kw in missing[:18]
            )
            st.markdown(f"<div style='margin-bottom: 12px;'>{pills}</div>", unsafe_allow_html=True)
        else:
            st.success("All major keywords from the job description are present!")

    if gap:
        with st.expander("🔍 Strategic Competency Gaps to Address", expanded=False):
            for skill in gap:
                st.markdown(f"- 📌 **{skill}** — highlighted in job requirements but missing or weak in your resume")