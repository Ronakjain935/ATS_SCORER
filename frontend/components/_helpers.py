def get_score_color(score: float):
    if score >= 80:
        return "#10B981", "rgba(16, 185, 129, 0.08)", "rgba(16, 185, 129, 0.25)"
    elif score >= 60:
        return "#F59E0B", "rgba(245, 158, 11, 0.08)", "rgba(245, 158, 11, 0.25)"
    else:
        return "#EF4444", "rgba(239, 68, 68, 0.08)", "rgba(239, 68, 68, 0.25)"


def get_score_emoji(score: float) -> str:
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    else:
        return "🔴"


def get_score_status(score: float) -> str:
    if score >= 85:
        return "OPTIMAL • READY TO APPLY"
    elif score >= 70:
        return "GOOD • MINOR ADJUSTMENTS RECOMMENDED"
    elif score >= 50:
        return "MODERATE • CRITICAL REVISIONS NEEDED"
    else:
        return "HIGH RISK • ATS REJECTION LIKELY"
