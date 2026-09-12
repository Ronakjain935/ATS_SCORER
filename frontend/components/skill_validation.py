from typing import Any, Dict

import streamlit as st


def display_skill_validation(analysis: Dict[str, Any]) -> None:
    details = analysis.get("skill_validation_details") or {}
    validated = details.get("validated", [])
    unvalidated = details.get("unvalidated", [])
    total = details.get("total", len(validated) + len(unvalidated))
    pct = details.get("validation_pct", 0.0)

    st.markdown("""
    <div style="margin-top: 1.25rem; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">✅</span>
            <span style="font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 700; color: #0F172A;">
                Neural Skill Validation & Proof of Work
            </span>
        </div>
        <p style="color: #64748B; font-size: 0.88rem; margin-top: 2px;">
            Validates whether skills listed in your skills section are genuinely backed by project bullet points
        </p>
    </div>
    """, unsafe_allow_html=True)

    if total == 0:
        st.info("No structured skills detected on the resume.")
        return

    # Modern 3-stat strip
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 16px; text-align: center;">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Total Detected Skills</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; color: #0F172A;">{total}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 12px 16px; text-align: center;">
            <div style="color: #059669; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Validated in Context</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; color: #10B981;">{len(validated)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        pct_color = "#10B981" if pct >= 75 else "#F59E0B" if pct >= 50 else "#EF4444"
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px 16px; text-align: center;">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">Context Backing Rate</div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; color: {pct_color};">{pct:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.progress(min(max(pct / 100.0, 0.0), 1.0))

    if validated:
        with st.expander(f"✨ Verified Skills ({len(validated)}) — Backed by Measurable Bullets", expanded=False):
            for entry in validated:
                skill = entry.get("skill", "?")
                projects = entry.get("projects", []) or []
                similarity = entry.get("similarity")
                project_text = ", ".join(projects[:2]) if projects else "experience bullets"
                sim_text = f" ({similarity * 100:.0f}% semantic alignment)" if isinstance(similarity, (int, float)) else ""
                st.markdown(f"- **{skill}**{sim_text} <br><span style='color: #64748B; font-size: 0.85rem;'>↳ Evidenced in: <i>{project_text}</i></span>", unsafe_allow_html=True)

    if unvalidated:
        with st.expander(f"⚠️ Unsubstantiated Skills ({len(unvalidated)}) — Mentioned without Context", expanded=False):
            st.caption("Recruiters and semantic ATS filters dock points when keywords are listed but absent from actual job duty descriptions.")
            pills_html = " ".join(
                f"<span style='display:inline-block; background:rgba(239,68,68,0.08); color:#DC2626; border:1px solid rgba(239,68,68,0.25); border-radius:9999px; padding:3px 10px; font-size:0.8rem; font-weight:600; margin:3px;'>{s}</span>"
                for s in unvalidated
            )
            st.markdown(f"<div style='margin-top:8px;'>{pills_html}</div>", unsafe_allow_html=True)