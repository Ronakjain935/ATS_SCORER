import io
import re
from typing import Any, Dict, List

import streamlit as st

from frontend.services.resume_generator import build_ats_resume_pdf, build_ats_resume_text


SAMPLE_PROFILE: Dict[str, Any] = {
    "name": "Ronak Jain",
    "target_title": "Full Stack Software Engineer",
    "email": "ronak.jain@example.com",
    "phone": "+91 98765 43210",
    "location": "Bangalore, India",
    "linkedin": "linkedin.com/in/ronakjain",
    "github": "github.com/ronakjain",
    "portfolio": "ronakjain.dev",
    "summary": (
        "Results-oriented Software Engineer with 3+ years of experience building scalable backend microservices, "
        "responsive web applications, and production machine learning pipelines. Demonstrated track record of optimizing "
        "API throughput by 40% and deploying mission-critical systems used by thousands of daily active users."
    ),
    "skills_languages": "Python, JavaScript, TypeScript, SQL, Go",
    "skills_frameworks": "FastAPI, Streamlit, React, Node.js, Flask, PyTorch",
    "skills_tools": "Docker, Kubernetes, AWS (S3, EC2), Git, PostgreSQL, Redis, CI/CD",
    "skills_soft": "System Architecture, Agile/Scrum, Technical Mentorship, Cross-Functional Collaboration",
    "exp_role_1": "Software Engineer",
    "exp_company_1": "Innovatech Solutions Pvt Ltd",
    "exp_location_1": "Bangalore, India",
    "exp_dates_1": "06/2022 – Present",
    "exp_bullets_1": (
        "• Architected and deployed 8+ REST microservices using FastAPI and Docker, handling 2.5M+ requests daily with 99.9% uptime.\n"
        "• Spearheaded backend migration from monolith to async microservices, reducing p99 latency from 320ms to 95ms.\n"
        "• Integrated PostgreSQL and Redis caching layers, cutting repetitive database query loads by 45%.\n"
        "• Automated CI/CD deployment pipelines using GitHub Actions, reducing release cycle time from 2 hours to 12 minutes."
    ),
    "exp_role_2": "Junior Software Developer",
    "exp_company_2": "Apex Cloud Systems",
    "exp_location_2": "Remote, India",
    "exp_dates_2": "07/2021 – 05/2022",
    "exp_bullets_2": (
        "• Developed reusable front-end dashboard modules in React and TypeScript, boosting customer onboarding speed by 30%.\n"
        "• Collaborated with senior engineers to implement JWT authentication and role-based access control (RBAC).\n"
        "• Authored comprehensive unit and integration test suites in pytest achieving 88% overall test coverage."
    ),
    "proj_title_1": "ATS Resume Scorer & Analyzer",
    "proj_tech_1": "Python, FastAPI, Streamlit, spaCy, SentenceTransformers, ReportLab",
    "proj_link_1": "github.com/ronakjain/ats-scorer",
    "proj_bullets_1": (
        "• Engineered end-to-end intelligent ATS resume analyzer calculating multi-dimensional match scores against job descriptions.\n"
        "• Implemented NLP semantic similarity matching and automated PDF report generation with fallback parsing engines."
    ),
    "proj_title_2": "Distributed Task Scheduler",
    "proj_tech_2": "Python, Redis, Docker, Celery, Prometheus",
    "proj_link_2": "github.com/ronakjain/distributed-scheduler",
    "proj_bullets_2": (
        "• Built an asynchronous distributed job queue system executing up to 10,000 tasks/min with automated worker failover.\n"
        "• Monitored real-time worker health and throughput metrics with Prometheus and Grafana alerting."
    ),
    "edu_degree": "Bachelor of Technology in Computer Science & Engineering",
    "edu_institution": "Visvesvaraya Technological University",
    "edu_dates": "2018 – 2022",
    "edu_details": "CGPA: 8.9/10 | First Class with Distinction",
    "certifications": (
        "• AWS Certified Solutions Architect – Associate (Amazon Web Services, 2023)\n"
        "• Professional Scrum Master I (Scrum.org, 2022)\n"
        "• Python for Data Science and Machine Learning (Coursera / DeepLearning.AI, 2021)"
    ),
    "achievements": (
        "• 1st Place Winner at National FinTech Hackathon 2023 out of 160+ participating engineering teams.\n"
        "• Awarded 'Employee of the Quarter' twice for outstanding technical delivery at Innovatech Solutions.\n"
        "• Ranked in the top 2% across 50,000+ candidates in National Engineering Aptitude Test."
    ),
}


def _get_field(key: str, default: str = "") -> str:
    return st.session_state.get(f"rb_{key}", default)


def _set_sample_data():
    for k, v in SAMPLE_PROFILE.items():
        st.session_state[f"rb_{k}"] = v
    st.session_state["rb_num_exp"] = 2
    st.session_state["rb_num_proj"] = 2
    st.session_state.pop("builder_pdf_bytes", None)
    st.session_state.pop("builder_text", None)


def _clear_data():
    keys_to_clear = [k for k in st.session_state if k.startswith("rb_")]
    for k in keys_to_clear:
        del st.session_state[k]
    st.session_state.pop("builder_pdf_bytes", None)
    st.session_state.pop("builder_text", None)


def render() -> None:
    st.title("📝 ATS-Friendly Resume Builder")
    st.markdown(
        "Generate a strictly ATS-optimized, single-column resume from your skills, experience, projects, and achievements. "
        "Tested for 100% parseability by ATS parsers."
    )

    # Top Control Bar
    col_c1, col_c2, col_c3 = st.columns([2, 1.2, 1.8])
    with col_c1:
        theme = st.selectbox(
            "🎨 Resume Accent Palette:",
            [
                "Modern Navy (#1A365D)",
                "Classic Charcoal (#2D3748)",
                "Slate Blue (#2B6CB0)",
                "Forest Green (#22543D)",
            ],
            key="rb_theme_select",
        )
        theme_hex = theme.split("(")[-1].rstrip(")")

    with col_c2:
        st.write("")
        st.write("")
        if st.button("✨ Load Sample Data", use_container_width=True, help="Fills the form with a high-scoring sample profile"):
            _set_sample_data()
            st.rerun()

    with col_c3:
        st.write("")
        st.write("")
        if st.button("🗑️ Clear Form", use_container_width=True, help="Resets all input fields"):
            _clear_data()
            st.rerun()

    st.markdown("---")

    # Tabs for structured input
    tabs = st.tabs([
        "👤 Personal Details",
        "🎯 Summary & Role",
        "💻 Skills",
        "💼 Experience",
        "🚀 Projects",
        "🎓 Education",
        "📜 Certifications & Honors",
    ])

    # 1. Personal Details
    with tabs[0]:
        st.subheader("Contact Information")
        p_c1, p_c2 = st.columns(2)
        with p_c1:
            name = st.text_input("Full Name *", value=_get_field("name"), placeholder="e.g. Ronak Jain", key="rb_name")
            target_title = st.text_input("Target Job Title / Headline *", value=_get_field("target_title"), placeholder="e.g. Senior Software Engineer", key="rb_target_title")
            email = st.text_input("Email Address *", value=_get_field("email"), placeholder="e.g. ronak@example.com", key="rb_email")
        with p_c2:
            phone = st.text_input("Phone Number *", value=_get_field("phone"), placeholder="e.g. +91 98765 43210", key="rb_phone")
            location = st.text_input("Location (City, State / Country)", value=_get_field("location"), placeholder="e.g. Bangalore, India", key="rb_location")
            linkedin = st.text_input("LinkedIn Profile URL", value=_get_field("linkedin"), placeholder="e.g. linkedin.com/in/ronakjain", key="rb_linkedin")

        p_c3, p_c4 = st.columns(2)
        with p_c3:
            github = st.text_input("GitHub Profile URL", value=_get_field("github"), placeholder="e.g. github.com/ronakjain", key="rb_github")
        with p_c4:
            portfolio = st.text_input("Portfolio / Website URL", value=_get_field("portfolio"), placeholder="e.g. ronakjain.dev", key="rb_portfolio")

    # 2. Summary & Role
    with tabs[1]:
        st.subheader("Professional Summary")
        st.caption("💡 **ATS Tip**: Write 3–4 sentences highlighting your years of experience, core technical stack, and standout quantifiable achievements.")
        summary = st.text_area(
            "Summary / Career Objective:",
            value=_get_field("summary"),
            height=140,
            placeholder="Seasoned Software Engineer with 4+ years of expertise in building...",
            key="rb_summary",
        )

    # 3. Skills
    with tabs[2]:
        st.subheader("Core Competencies & Categorized Skills")
        st.caption("💡 **ATS Tip**: Use standard industry skill keywords separated by commas.")
        s_c1, s_c2 = st.columns(2)
        with s_c1:
            skills_languages = st.text_input(
                "Programming Languages:",
                value=_get_field("skills_languages"),
                placeholder="e.g. Python, SQL, JavaScript, Go",
                key="rb_skills_languages",
            )
            skills_frameworks = st.text_input(
                "Frameworks & Libraries:",
                value=_get_field("skills_frameworks"),
                placeholder="e.g. FastAPI, React, Django, PyTorch",
                key="rb_skills_frameworks",
            )
        with s_c2:
            skills_tools = st.text_input(
                "Tools, Cloud & Databases:",
                value=_get_field("skills_tools"),
                placeholder="e.g. Docker, AWS, PostgreSQL, Git, Redis",
                key="rb_skills_tools",
            )
            skills_soft = st.text_input(
                "Methodologies & Core Competencies:",
                value=_get_field("skills_soft"),
                placeholder="e.g. Microservices, Agile/Scrum, System Design",
                key="rb_skills_soft",
            )

    # 4. Work Experience
    with tabs[3]:
        st.subheader("Work Experience")
        st.caption("💡 **ATS Tip**: Start each bullet point with strong action verbs (Architected, Developed, Led, Spearheaded) and include numbers/metrics.")

        num_exp = st.selectbox("Number of Experience Entries:", [1, 2, 3, 4], index=st.session_state.get("rb_num_exp", 1) - 1, key="rb_num_exp_select")
        st.session_state["rb_num_exp"] = num_exp

        experience_entries = []
        for i in range(1, num_exp + 1):
            with st.expander(f"💼 Experience #{i}", expanded=(i == 1)):
                e_c1, e_c2 = st.columns(2)
                with e_c1:
                    exp_role = st.text_input(f"Job Title #{i}", value=_get_field(f"exp_role_{i}"), placeholder="e.g. Software Engineer", key=f"rb_exp_role_{i}")
                    exp_comp = st.text_input(f"Company Name #{i}", value=_get_field(f"exp_company_{i}"), placeholder="e.g. Acme Corp", key=f"rb_exp_company_{i}")
                with e_c2:
                    exp_dates = st.text_input(f"Employment Dates #{i}", value=_get_field(f"exp_dates_{i}"), placeholder="e.g. 05/2022 – Present", key=f"rb_exp_dates_{i}")
                    exp_loc = st.text_input(f"Location #{i}", value=_get_field(f"exp_location_{i}"), placeholder="e.g. New York, NY", key=f"rb_exp_location_{i}")

                exp_bullets = st.text_area(
                    f"Responsibilities & Achievements #{i} (one bullet per line):",
                    value=_get_field(f"exp_bullets_{i}"),
                    height=120,
                    placeholder="• Developed high-throughput REST APIs reducing response times by 35%.\n• Collaborated with cross-functional teams to deploy 5 client features.",
                    key=f"rb_exp_bullets_{i}",
                )
                if exp_role or exp_comp:
                    experience_entries.append({
                        "job_title": exp_role,
                        "company": exp_comp,
                        "location": exp_loc,
                        "dates": exp_dates,
                        "bullets": exp_bullets,
                    })

    # 5. Projects
    with tabs[4]:
        st.subheader("Key Projects")
        st.caption("💡 **ATS Tip**: Include the technologies used in brackets or listed clearly so ATS algorithms parse and match project skills.")

        num_proj = st.selectbox("Number of Projects:", [1, 2, 3, 4], index=st.session_state.get("rb_num_proj", 1) - 1, key="rb_num_proj_select")
        st.session_state["rb_num_proj"] = num_proj

        project_entries = []
        for j in range(1, num_proj + 1):
            with st.expander(f"🚀 Project #{j}", expanded=(j == 1)):
                pj_c1, pj_c2 = st.columns(2)
                with pj_c1:
                    pj_title = st.text_input(f"Project Title #{j}", value=_get_field(f"proj_title_{j}"), placeholder="e.g. Real-Time Chat Engine", key=f"rb_proj_title_{j}")
                    pj_tech = st.text_input(f"Technologies Used #{j}", value=_get_field(f"proj_tech_{j}"), placeholder="e.g. Python, WebSockets, Redis, Docker", key=f"rb_proj_tech_{j}")
                with pj_c2:
                    pj_link = st.text_input(f"Project Link / Repo #{j}", value=_get_field(f"proj_link_{j}"), placeholder="e.g. github.com/user/chat-engine", key=f"rb_proj_link_{j}")

                pj_bullets = st.text_area(
                    f"Project Description & Highlights #{j} (one bullet per line):",
                    value=_get_field(f"proj_bullets_{j}"),
                    height=100,
                    placeholder="• Built asynchronous messaging server supporting 5,000 concurrent sockets.\n• Implemented end-to-end encryption and persistence in MongoDB.",
                    key=f"rb_proj_bullets_{j}",
                )
                if pj_title:
                    project_entries.append({
                        "title": pj_title,
                        "technologies": pj_tech,
                        "link": pj_link,
                        "bullets": pj_bullets,
                    })

    # 6. Education
    with tabs[5]:
        st.subheader("Education")
        ed_c1, ed_c2 = st.columns(2)
        with ed_c1:
            edu_degree = st.text_input("Degree & Major *", value=_get_field("edu_degree"), placeholder="e.g. B.Tech in Computer Science", key="rb_edu_degree")
            edu_institution = st.text_input("University / College *", value=_get_field("edu_institution"), placeholder="e.g. State University", key="rb_edu_institution")
        with ed_c2:
            edu_dates = st.text_input("Graduation Year / Dates", value=_get_field("edu_dates"), placeholder="e.g. 2018 – 2022", key="rb_edu_dates")
            edu_details = st.text_input("GPA / Honors / Key Coursework", value=_get_field("edu_details"), placeholder="e.g. GPA: 3.8/4.0 | Dean's List", key="rb_edu_details")

    # 7. Certifications & Honors
    with tabs[6]:
        st.subheader("Certifications, Licenses & Achievements")
        st.caption("💡 **ATS Tip**: List credentials clearly with issuing body and year.")
        certifications = st.text_area(
            "Certifications (one per line):",
            value=_get_field("certifications"),
            height=110,
            placeholder="• AWS Certified Solutions Architect (2023)\n• Certified Kubernetes Administrator (CKA, 2022)",
            key="rb_certifications",
        )
        achievements = st.text_area(
            "Honors, Awards & Achievements (one per line):",
            value=_get_field("achievements"),
            height=110,
            placeholder="• Winner of University Hackathon 2023\n• Published research paper on NLP in IEEE Journal",
            key="rb_achievements",
        )

    st.markdown("---")

    # Assembling skills dictionary
    categorized_skills = {}
    if skills_languages:
        categorized_skills["Languages"] = [s.strip() for s in skills_languages.split(",") if s.strip()]
    if skills_frameworks:
        categorized_skills["Frameworks & Libraries"] = [s.strip() for s in skills_frameworks.split(",") if s.strip()]
    if skills_tools:
        categorized_skills["Cloud, Databases & Tools"] = [s.strip() for s in skills_tools.split(",") if s.strip()]
    if skills_soft:
        categorized_skills["Core Competencies"] = [s.strip() for s in skills_soft.split(",") if s.strip()]

    # Parse certifications into list
    cert_list = [c.strip() for c in certifications.split("\n") if c.strip()]
    ach_list = [a.strip() for a in achievements.split("\n") if a.strip()]

    education_list = []
    if edu_degree or edu_institution:
        education_list.append({
            "degree": edu_degree,
            "institution": edu_institution,
            "dates": edu_dates,
            "details": edu_details,
        })

    resume_payload = {
        "name": name or "Your Name",
        "target_title": target_title,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "portfolio": portfolio,
        "summary": summary,
        "skills": categorized_skills,
        "experience": experience_entries,
        "projects": project_entries,
        "education": education_list,
        "certifications": cert_list,
        "achievements": ach_list,
    }

    # Generate Buttons
    _, mid_btn, _ = st.columns([1, 2, 1])
    with mid_btn:
        generate_clicked = st.button(
            "🚀 Generate ATS-Optimized Resume",
            use_container_width=True,
            type="primary",
            key="btn_generate_resume",
        )

    if generate_clicked:
        if not name:
            st.error("Please provide at least your Full Name in the Personal Details tab.")
            return

        with st.spinner("Compiling ATS-compliant resume with ReportLab..."):
            pdf_bytes = build_ats_resume_pdf(resume_payload, theme_color=theme_hex)
            txt_content = build_ats_resume_text(resume_payload)

        st.session_state["builder_pdf_bytes"] = pdf_bytes
        st.session_state["builder_text"] = txt_content
        st.session_state["builder_payload"] = resume_payload
        st.success("✅ ATS-Friendly Resume generated successfully!")

    # Display results & downloads if generated
    if "builder_pdf_bytes" in st.session_state:
        st.markdown("### 📥 Download & Verification Options")

        d_c1, d_c2, d_c3 = st.columns(3)

        with d_c1:
            safe_name = re.sub(r"[^\w\-_]", "_", name or "Resume")
            st.download_button(
                "⬇️ Download ATS PDF",
                data=st.session_state["builder_pdf_bytes"],
                file_name=f"{safe_name}_ATS_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
                key="download_builder_pdf",
            )

        with d_c2:
            st.download_button(
                "📋 Download Plain Text (.txt)",
                data=st.session_state["builder_text"],
                file_name=f"{safe_name}_ATS_Resume.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_builder_txt",
            )

        with d_c3:
            # Transfer directly to the ATS Scorer panel
            if st.button("⚡ Score in ATS Scorer", use_container_width=True, help="Sends this generated resume directly to the ATS Scorer to check its score"):
                class InMemoryUploadedFile:
                    def __init__(self, filename: str, data: bytes):
                        self.name = filename
                        self.data = data
                        self.size = len(data)
                        self.type = "application/pdf"

                    def getvalue(self):
                        return self.data

                    def read(self):
                        return self.data

                # Inject into scorer upload state
                st.session_state["scorer_injected_resume"] = InMemoryUploadedFile(
                    f"{safe_name}_ATS_Resume.pdf",
                    st.session_state["builder_pdf_bytes"]
                )
                st.session_state["current_view"] = "scorer"
                st.rerun()

        # On-screen visual preview
        st.markdown("---")
        st.markdown("### 👁️ Resume Content Preview")
        with st.expander("📄 View Generated Resume Text", expanded=True):
            st.code(st.session_state["builder_text"], language="markdown")
