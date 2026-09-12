import streamlit as st


def render():
    """Render the revamped modern resources and tips page"""
    
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.6rem; font-weight: 800; background: linear-gradient(135deg, #1E1B4B 0%, #4F46E5 50%, #7C3AED 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 6px;">
            📚 ATS Master Guide & Cheat Sheet
        </h1>
        <p style="color: #64748B; font-size: 1.05rem;">
            The definitive blueprint for beating applicant tracking algorithms and landing interview callbacks.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ATS Tips Comparison
    st.markdown("### 🎯 Critical ATS Rules: Do's vs Don'ts")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 16px; padding: 1.5rem; height: 100%;">
            <div style="color: #166534; font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span>✅ Golden Rules (Do's)</span>
            </div>
            <ul style="color: #14532D; font-size: 0.92rem; line-height: 1.7; padding-left: 1.2rem; margin-bottom: 0;">
                <li><strong>Use Conventional Headings:</strong> 'Work Experience', 'Education', 'Technical Skills'.</li>
                <li><strong>Quantify Real Impact:</strong> 'Boosted conversion by 23%' instead of 'worked on sales'.</li>
                <li><strong>Direct JD Keyword Alignment:</strong> Include exact terms mentioned in the job post.</li>
                <li><strong>Clean Standard Fonts:</strong> Arial, Calibri, Helvetica, or Times New Roman.</li>
                <li><strong>Single-Column Hierarchy:</strong> Read top-to-bottom without multi-column breaks.</li>
                <li><strong>Verified File Formats:</strong> Submit clean, parseable .PDF or .DOCX files.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 16px; padding: 1.5rem; height: 100%;">
            <div style="color: #991B1B; font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span>❌ Instant Disqualifiers (Don'ts)</span>
            </div>
            <ul style="color: #7F1D1D; font-size: 0.92rem; line-height: 1.7; padding-left: 1.2rem; margin-bottom: 0;">
                <li><strong>No Tables or Nested Cells:</strong> Screen-readers and parsers merge cells into gibberish.</li>
                <li><strong>Never Put Info in Headers/Footers:</strong> Many ATS engines omit header/footer bands completely.</li>
                <li><strong>Avoid Skill Progress Bars:</strong> '90% Python' means nothing to a keyword extractor.</li>
                <li><strong>Zero Unparsed Graphics:</strong> No icons, logos, profile photos, or embedded infographics.</li>
                <li><strong>No Invisible Keyword Stuffing:</strong> White text hacks get flagged as fraud immediately.</li>
                <li><strong>Avoid Unexplained Acronyms:</strong> Always write out 'Continuous Integration (CI)'.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Industry Keywords
    st.markdown("### 🔑 High-Frequency ATS Keywords by Field")
    st.caption("Common taxonomy terms frequently filtered by recruiters across top industries.")

    tab1, tab2, tab3, tab4 = st.tabs(["💻 Software & Cloud", "🧠 Data & AI", "💼 Product & Business", "🎨 Design & UX"])

    with tab1:
        st.markdown("""
        **Core Languages & Frameworks:**
        `Python` `TypeScript` `JavaScript` `Java` `Go` `Rust` `React` `Next.js` `Node.js` `FastAPI` `Django`

        **Cloud, Infrastructure & DevOps:**
        `AWS (EC2, S3, Lambda)` `Docker` `Kubernetes` `Terraform` `CI/CD Pipelines` `GitHub Actions` `Microservices` `PostgreSQL` `Redis` `GraphQL` `RESTful APIs`

        **Methodologies:**
        `Agile/Scrum` `Test-Driven Development (TDD)` `System Architecture` `Observability` `Distributed Systems`
        """)

    with tab2:
        st.markdown("""
        **Machine Learning & Modeling:**
        `PyTorch` `TensorFlow` `Scikit-Learn` `NLP` `Hugging Face` `Transformers` `LLM Fine-Tuning` `RAG` `Computer Vision`

        **Data Engineering & Analytics:**
        `SQL` `Pandas` `Apache Spark` `Snowflake` `BigQuery` `dbt` `Kafka` `Airflow` `Data Pipelines` `A/B Testing` `Statistical Modeling`
        """)

    with tab3:
        st.markdown("""
        **Product Strategy & Execution:**
        `Product Roadmap` `User Journey Mapping` `Cross-Functional Leadership` `OKRs` `KPI Tracking` `PRD Writing`

        **Business Operations & Growth:**
        `Stakeholder Management` `Customer Acquisition Cost (CAC)` `LTV Optimization` `Market Research` `Go-To-Market (GTM) Strategy` `Risk Management` `Revenue Forecasting`
        """)

    with tab4:
        st.markdown("""
        **Design & Prototyping Tools:**
        `Figma` `Design Systems` `Wireframing` `Rapid Prototyping` `User Personas` `Interactive UI` `Accessibility (WCAG)`

        **Research & Strategy:**
        `Usability Testing` `Information Architecture` `Qualitative Interviews` `Heuristic Evaluation` `Interaction Design`
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pre-Flight Application Checklist
    st.markdown("### ✈️ Pre-Flight Application Checklist")
    st.caption("Run through these 5 quick checks right before hitting 'Submit':")

    c1, c2 = st.columns(2)
    with c1:
        st.checkbox("File is saved cleanly as PDF or DOCX under 5 MB", value=True)
        st.checkbox("Contact info (Phone, Email, LinkedIn, City/Country) is at top of body", value=True)
        st.checkbox("Every work experience item contains at least 2 quantified metrics", value=True)
    with c2:
        st.checkbox("Core keywords from target job description appear naturally in bullets", value=True)
        st.checkbox("No multi-column graphics, text boxes, or embedded photo charts", value=True)
        st.checkbox("File was tested through ATS Scorer and scored 80+ points", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Next steps card
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 16px; padding: 2rem; text-align: center;">
        <h3 style="font-family: 'Outfit', sans-serif; margin-bottom: 8px; color: #1E1B4B;">Ready to craft your resume?</h3>
        <p style="color: #64748B; margin-bottom: 1.25rem;">Use our built-in ATS Resume Builder to generate guaranteed parseable documents instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    _, mid_btn, _ = st.columns([1, 2, 1])
    with mid_btn:
        if st.button("📝 Open Resume Builder", use_container_width=True, type="primary"):
            st.session_state.current_view = "builder"
            st.rerun()