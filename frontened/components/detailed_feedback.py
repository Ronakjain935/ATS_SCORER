from typing import Any, Dict, List
import streamlit as st


def display_detailed_feedback(analysis: Dict[str, Any]) -> None:
    feedback_items: List[Dict[str, Any]] = analysis.get("detailed_feedback") or []
    if not feedback_items:
        return

    st.markdown("### 🔍 Detailed Feedback & Fixes")
    st.caption("Specific issues identified in your resume with actionable solutions.")

    for item in feedback_items:
        title = item.get("issue_title", "Issue")
        severity = (item.get("severity_level") or "low").lower()

        with st.expander(f"**{title}** — {severity.upper()}", expanded=severity in ("critical", "high")):
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**ATS Impact:** {item.get('ats_impact', 'N/A')}")
                if item.get("where_it_appears"):
                    st.markdown(f"**Found in:** `{item.get('where_it_appears')}`")
            with col2:
                st.markdown(f"**Severity Level:** `{severity.upper()}`")

            st.markdown(f"**Why this matters:** {item.get('explanation', '')}")
            st.markdown(f"**How to fix:** {item.get('how_to_fix', '')}")

            example = item.get("example_improvement")
            if example:
                st.info(f"💡 **Example Improvement:**\n\n```\n{example}\n```")

            action_items = item.get("action_items") or []
            if action_items:
                st.markdown("**Action Checklist:**")
                for action in action_items:
                    st.markdown(f"- [ ] {action}")