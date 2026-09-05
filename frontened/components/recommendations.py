from typing import Any, Dict, List
import streamlit as st


def display_recommendations(analysis: Dict[str, Any]) -> None:
    suggestions: List[Any] = analysis.get("suggestions") or analysis.get("recommendations") or []
    if not suggestions:
        return

    st.markdown("### 💡 Strategic Recommendations")
    st.caption("Tailored suggestions to make your resume stand out to recruiters and hiring managers.")

    for idx, item in enumerate(suggestions, 1):
        if isinstance(item, dict):
            title = item.get("title", f"Recommendation #{idx}")
            desc = item.get("description", "")
            priority = str(item.get("priority", "medium")).lower()
            st.markdown(f"#### {idx}. {title}")
            if desc:
                st.markdown(desc)
            actions = item.get("action_items") or []
            if actions:
                for action in actions:
                    st.markdown(f"- {action}")
        else:
            st.markdown(f"**{idx}.** {item}")