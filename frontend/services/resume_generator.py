import io
import re
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _clean_text(text: Any) -> str:
    if not text:
        return ""
    # Strip HTML tags or raw XML entities that break ReportLab Paragraph
    s = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.strip()


def build_ats_resume_pdf(data: Dict[str, Any], theme_color: str = "#1A365D") -> bytes:
    """
    Generates a single-column, strictly ATS-compliant PDF resume using ReportLab.
    Ensures standard font sizes, clear section hierarchy, and parseable text streams.
    """
    buffer = io.BytesIO()

    # 0.5 inch (36 pt) margins for optimal ATS scanning and printable area
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    primary_color = colors.HexColor(theme_color)
    dark_neutral = colors.HexColor("#2D3748")
    subtle_neutral = colors.HexColor("#718096")

    # Typography Styles
    name_style = ParagraphStyle(
        "ATSName",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=0,
    )
    title_style = ParagraphStyle(
        "ATSTitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=dark_neutral,
        alignment=0,
    )
    contact_style = ParagraphStyle(
        "ATSContact",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=subtle_neutral,
        alignment=0,
    )
    section_heading = ParagraphStyle(
        "ATSSectionHeading",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=8,
        spaceAfter=2,
    )
    body_bold = ParagraphStyle(
        "ATSBodyBold",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=dark_neutral,
    )
    body_regular = ParagraphStyle(
        "ATSBodyRegular",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=dark_neutral,
    )
    body_italic = ParagraphStyle(
        "ATSBodyItalic",
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12,
        textColor=subtle_neutral,
    )
    bullet_style = ParagraphStyle(
        "ATSBullet",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        leftIndent=14,
        firstLineIndent=-10,
        textColor=dark_neutral,
    )

    def add_section_divider(heading_text: str):
        story.append(Spacer(1, 6))
        story.append(Paragraph(heading_text.upper(), section_heading))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=primary_color,
                spaceBefore=2,
                spaceAfter=6,
            )
        )

    # 1. Header (Name, Job Title, Contact Information)
    name = _clean_text(data.get("name") or "Your Name")
    story.append(Paragraph(name, name_style))

    target_title = _clean_text(data.get("target_title") or data.get("headline") or "")
    if target_title:
        story.append(Paragraph(target_title, title_style))
        story.append(Spacer(1, 2))

    contact_parts = []
    if data.get("email"):
        contact_parts.append(_clean_text(data["email"]))
    if data.get("phone"):
        contact_parts.append(_clean_text(data["phone"]))
    if data.get("location"):
        contact_parts.append(_clean_text(data["location"]))
    if data.get("linkedin"):
        contact_parts.append(_clean_text(data["linkedin"]))
    if data.get("github"):
        contact_parts.append(_clean_text(data["github"]))
    if data.get("portfolio"):
        contact_parts.append(_clean_text(data["portfolio"]))

    if contact_parts:
        contact_line = " &nbsp;|&nbsp; ".join(contact_parts)
        story.append(Paragraph(contact_line, contact_style))

    # 2. Professional Summary
    summary = _clean_text(data.get("summary") or "")
    if summary:
        add_section_divider("Professional Summary")
        story.append(Paragraph(summary, body_regular))

    # 3. Core Competencies & Technical Skills
    skills_data = data.get("skills") or {}
    has_skills = bool(skills_data)

    if has_skills:
        add_section_divider("Technical & Core Skills")
        if isinstance(skills_data, dict):
            for category, items in skills_data.items():
                if items:
                    if isinstance(items, list):
                        items_str = ", ".join(items)
                    else:
                        items_str = str(items)
                    line_html = f"<b>{_clean_text(category)}:</b> {_clean_text(items_str)}"
                    story.append(Paragraph(line_html, body_regular))
                    story.append(Spacer(1, 2))
        elif isinstance(skills_data, list):
            skills_str = ", ".join(skills_data)
            story.append(Paragraph(f"<b>Key Skills:</b> {_clean_text(skills_str)}", body_regular))

    # 4. Work Experience
    experience_list = data.get("experience") or []
    if experience_list:
        add_section_divider("Work Experience")
        for idx, exp in enumerate(experience_list):
            job_title = _clean_text(exp.get("job_title") or exp.get("role") or "")
            company = _clean_text(exp.get("company") or "")
            location = _clean_text(exp.get("location") or "")
            dates = _clean_text(exp.get("dates") or exp.get("duration") or "")

            title_left = f"<b>{job_title}</b>"
            if company:
                title_left += f" &nbsp;|&nbsp; {company}"
            if location:
                title_left += f" &nbsp;({location})"

            # Top row: Role & Company on left, Dates on right
            row_data = [
                [Paragraph(title_left, body_bold), Paragraph(dates, body_italic)]
            ]
            exp_table = Table(row_data, colWidths=[380, 160])
            exp_table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ])
            )
            story.append(exp_table)

            # Bullet points
            bullets = exp.get("bullets") or exp.get("description") or []
            if isinstance(bullets, str):
                bullets = [b.strip() for b in bullets.split("\n") if b.strip()]

            for bullet in bullets:
                clean_b = _clean_text(re.sub(r"^[-•*–\s]+", "", bullet))
                if clean_b:
                    story.append(Paragraph(f"&bull; &nbsp;{clean_b}", bullet_style))

            if idx < len(experience_list) - 1:
                story.append(Spacer(1, 6))

    # 5. Projects
    projects_list = data.get("projects") or []
    if projects_list:
        add_section_divider("Key Projects")
        for idx, proj in enumerate(projects_list):
            p_title = _clean_text(proj.get("title") or proj.get("name") or "")
            p_tech = _clean_text(proj.get("technologies") or proj.get("tech_stack") or "")
            p_link = _clean_text(proj.get("link") or proj.get("url") or "")

            left_content = f"<b>{p_title}</b>"
            if p_tech:
                left_content += f" &nbsp;[{p_tech}]"

            row_data = [
                [Paragraph(left_content, body_bold), Paragraph(p_link, body_italic)]
            ]
            proj_table = Table(row_data, colWidths=[380, 160])
            proj_table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ])
            )
            story.append(proj_table)

            p_desc = proj.get("bullets") or proj.get("description") or []
            if isinstance(p_desc, str):
                p_desc = [b.strip() for b in p_desc.split("\n") if b.strip()]

            for bullet in p_desc:
                clean_b = _clean_text(re.sub(r"^[-•*–\s]+", "", bullet))
                if clean_b:
                    story.append(Paragraph(f"&bull; &nbsp;{clean_b}", bullet_style))

            if idx < len(projects_list) - 1:
                story.append(Spacer(1, 5))

    # 6. Education
    education_list = data.get("education") or []
    if education_list:
        add_section_divider("Education")
        for idx, edu in enumerate(education_list):
            degree = _clean_text(edu.get("degree") or "")
            institution = _clean_text(edu.get("institution") or edu.get("school") or "")
            dates = _clean_text(edu.get("dates") or edu.get("year") or "")
            details = _clean_text(edu.get("details") or edu.get("gpa") or "")

            edu_left = f"<b>{degree}</b>"
            if institution:
                edu_left += f", {institution}"

            row_data = [
                [Paragraph(edu_left, body_bold), Paragraph(dates, body_italic)]
            ]
            edu_table = Table(row_data, colWidths=[400, 140])
            edu_table.setStyle(
                TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ])
            )
            story.append(edu_table)
            if details:
                story.append(Paragraph(details, body_regular))

            if idx < len(education_list) - 1:
                story.append(Spacer(1, 4))

    # 7. Certifications & Licenses
    certs_list = data.get("certifications") or []
    if certs_list:
        add_section_divider("Certifications & Licenses")
        for cert in certs_list:
            if isinstance(cert, dict):
                c_name = _clean_text(cert.get("title") or cert.get("name") or "")
                c_issuer = _clean_text(cert.get("issuer") or "")
                c_year = _clean_text(cert.get("year") or "")
                txt = f"&bull; &nbsp;<b>{c_name}</b>"
                if c_issuer:
                    txt += f" &mdash; {c_issuer}"
                if c_year:
                    txt += f" ({c_year})"
                story.append(Paragraph(txt, bullet_style))
            else:
                story.append(Paragraph(f"&bull; &nbsp;{_clean_text(cert)}", bullet_style))

    # 8. Key Achievements & Awards
    achievements = data.get("achievements") or []
    if achievements:
        add_section_divider("Honors & Achievements")
        if isinstance(achievements, str):
            achievements = [a.strip() for a in achievements.split("\n") if a.strip()]
        for ach in achievements:
            clean_a = _clean_text(re.sub(r"^[-•*–\s]+", "", str(ach)))
            if clean_a:
                story.append(Paragraph(f"&bull; &nbsp;{clean_a}", bullet_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def build_ats_resume_text(data: Dict[str, Any]) -> str:
    """
    Generates a clean, plain text resume suitable for direct copy-paste into ATS portals.
    """
    lines = []

    # Header
    name = data.get("name", "Your Name")
    lines.append(name.upper())
    title = data.get("target_title") or data.get("headline") or ""
    if title:
        lines.append(title)

    contacts = []
    for key in ["email", "phone", "location", "linkedin", "github", "portfolio"]:
        val = data.get(key)
        if val:
            contacts.append(val)
    if contacts:
        lines.append(" | ".join(contacts))

    lines.append("=" * 60)
    lines.append("")

    # Summary
    if data.get("summary"):
        lines.append("PROFESSIONAL SUMMARY")
        lines.append("-" * 30)
        lines.append(data["summary"].strip())
        lines.append("")

    # Skills
    if data.get("skills"):
        lines.append("SKILLS & COMPETENCIES")
        lines.append("-" * 30)
        skills_data = data["skills"]
        if isinstance(skills_data, dict):
            for cat, items in skills_data.items():
                items_str = ", ".join(items) if isinstance(items, list) else str(items)
                lines.append(f"{cat}: {items_str}")
        elif isinstance(skills_data, list):
            lines.append(", ".join(skills_data))
        lines.append("")

    # Experience
    if data.get("experience"):
        lines.append("WORK EXPERIENCE")
        lines.append("-" * 30)
        for exp in data["experience"]:
            role = exp.get("job_title") or exp.get("role") or ""
            comp = exp.get("company") or ""
            dates = exp.get("dates") or exp.get("duration") or ""
            loc = exp.get("location") or ""

            header = f"{role} | {comp}"
            if loc:
                header += f" ({loc})"
            if dates:
                header += f" | {dates}"
            lines.append(header)

            bullets = exp.get("bullets") or exp.get("description") or []
            if isinstance(bullets, str):
                bullets = [b.strip() for b in bullets.split("\n") if b.strip()]
            for b in bullets:
                clean_b = re.sub(r"^[-•*–\s]+", "", b)
                lines.append(f"  * {clean_b}")
            lines.append("")

    # Projects
    if data.get("projects"):
        lines.append("KEY PROJECTS")
        lines.append("-" * 30)
        for proj in data["projects"]:
            title = proj.get("title") or proj.get("name") or ""
            tech = proj.get("technologies") or proj.get("tech_stack") or ""
            link = proj.get("link") or proj.get("url") or ""

            header = title
            if tech:
                header += f" [{tech}]"
            if link:
                header += f" ({link})"
            lines.append(header)

            bullets = proj.get("bullets") or proj.get("description") or []
            if isinstance(bullets, str):
                bullets = [b.strip() for b in bullets.split("\n") if b.strip()]
            for b in bullets:
                clean_b = re.sub(r"^[-•*–\s]+", "", b)
                lines.append(f"  * {clean_b}")
            lines.append("")

    # Education
    if data.get("education"):
        lines.append("EDUCATION")
        lines.append("-" * 30)
        for edu in data["education"]:
            deg = edu.get("degree") or ""
            inst = edu.get("institution") or edu.get("school") or ""
            year = edu.get("dates") or edu.get("year") or ""
            gpa = edu.get("details") or edu.get("gpa") or ""

            line = deg
            if inst:
                line += f", {inst}"
            if year:
                line += f" ({year})"
            lines.append(line)
            if gpa:
                lines.append(f"  {gpa}")
        lines.append("")

    # Certifications
    if data.get("certifications"):
        lines.append("CERTIFICATIONS")
        lines.append("-" * 30)
        for cert in data["certifications"]:
            if isinstance(cert, dict):
                c_name = cert.get("title") or cert.get("name") or ""
                c_iss = cert.get("issuer") or ""
                c_yr = cert.get("year") or ""
                lines.append(f"  * {c_name} - {c_iss} ({c_yr})".strip(" -()"))
            else:
                lines.append(f"  * {cert}")
        lines.append("")

    # Achievements
    if data.get("achievements"):
        lines.append("HONORS & ACHIEVEMENTS")
        lines.append("-" * 30)
        achs = data["achievements"]
        if isinstance(achs, str):
            achs = [a.strip() for a in achs.split("\n") if a.strip()]
        for ach in achs:
            clean_a = re.sub(r"^[-•*–\s]+", "", str(ach))
            lines.append(f"  * {clean_a}")
        lines.append("")

    return "\n".join(lines)
