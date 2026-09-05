def get_score_color(score: float):
    if score >= 80:
        return "#16a34a", "#f0fdf4"
    elif score >= 60:
        return "#d97706", "#fffbeb"
    else:
        return "#dc2626", "#fef2f2"


def get_score_emoji(score: float) -> str:
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    else:
        return "🔴"
