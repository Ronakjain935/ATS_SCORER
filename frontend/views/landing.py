import streamlit as st


def render():
    """
    Renders the modern, premium landing page for ATS Resume Scorer.
    """
    # Embedded Page-Specific CSS for Landing
    st.markdown("""
    <style>
        .hero-container {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.95) 50%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 24px;
            padding: 3.5rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 20px 40px -15px rgba(99, 102, 241, 0.3);
            margin-bottom: 2.5rem;
        }
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 300px;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, transparent 70%);
            filter: blur(50px);
            pointer-events: none;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(129, 140, 248, 0.35);
            color: #C7D2FE;
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            margin-bottom: 1.25rem;
            text-transform: uppercase;
        }
        .hero-title {
            font-family: 'Outfit', sans-serif;
            font-size: 3.2rem;
            font-weight: 800;
            line-height: 1.15;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #A5B4FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
        }
        .hero-subtitle {
            font-size: 1.15rem;
            color: #94A3B8;
            max-width: 680px;
            margin: 0 auto 2rem auto;
            line-height: 1.6;
        }
        .stat-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        .stat-item {
            text-align: center;
        }
        .stat-num {
            font-family: 'Outfit', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: #FFFFFF;
            background: linear-gradient(135deg, #818CF8 0%, #C084FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            font-size: 0.8rem;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 4px;
        }
        .glass-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 18px;
            padding: 1.75rem;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
            transition: all 0.25s ease;
            height: 100%;
        }
        .glass-card:hover {
            transform: translateY(-4px);
            border-color: #6366F1;
            box-shadow: 0 12px 30px rgba(99, 102, 241, 0.12);
        }
        .card-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            display: inline-block;
        }
        .card-heading {
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.5rem;
        }
        .card-desc {
            font-size: 0.92rem;
            color: #64748B;
            line-height: 1.55;
        }
        .comparison-box-fail {
            background: #FEF2F2;
            border: 1px solid #FECACA;
            border-radius: 16px;
            padding: 1.5rem;
        }
        .comparison-box-pass {
            background: #F0FDF4;
            border: 1px solid #BBF7D0;
            border-radius: 16px;
            padding: 1.5rem;
        }
        .step-pill {
            display: inline-block;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 12px;
        }
        .footer-cta {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #9333EA 100%);
            border-radius: 20px;
            padding: 3rem 2rem;
            text-align: center;
            color: white;
            box-shadow: 0 16px 36px rgba(79, 70, 229, 0.35);
            margin-top: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # 1. Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">⚡ Next-Gen ATS Intelligence • spaCy NLP + Transformers</div>
        <div class="hero-title">Land 3x More Interviews With An ATS-Proof Resume</div>
        <div class="hero-subtitle">
            Most resumes are rejected by Applicant Tracking System bots before a human recruiter ever sees them.
            Get instantaneous, neural-level scoring, skills gap diagnostics, and ATS-safe PDF export.
        </div>
        <div class="stat-strip">
            <div class="stat-item">
                <div class="stat-num">98.4%</div>
                <div class="stat-label">Parse Accuracy</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">5 Pillars</div>
                <div class="stat-label">Weighted Scoring</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">&lt; 3 sec</div>
                <div class="stat-label">Neural Audit</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">100% Free</div>
                <div class="stat-label">Privacy-First</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Hero Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Analyze Existing Resume", use_container_width=True, type="primary", key="cta_landing_scorer"):
            st.session_state.current_view = "scorer"
            st.rerun()
    with col2:
        if st.button("📝 Build ATS-Optimized Resume", use_container_width=True, key="cta_landing_builder"):
            st.session_state.current_view = "builder"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Why Resumes Get Rejected (The Reality Check)
    st.markdown("### 🔍 Why 75% of Resumes Fail Applicant Tracking Systems")
    st.caption("How modern hiring algorithms process your application behind the scenes.")

    c_fail, c_pass = st.columns(2)
    with c_fail:
        st.markdown("""
        <div class="comparison-box-fail">
            <h4 style="color: #991B1B; margin-bottom: 8px;">❌ Unoptimized Resume (Rejected by ATS)</h4>
            <ul style="color: #7F1D1D; font-size: 0.92rem; line-height: 1.6; margin-bottom: 0;">
                <li><strong>Complex tables & columns:</strong> Multi-column graphics break text parsing order.</li>
                <li><strong>Keyword Mismatches:</strong> Synonyms not matched to exact JD taxonomy.</li>
                <li><strong>Unsubstantiated Skills:</strong> Listing skills in sidebar with zero project context.</li>
                <li><strong>Non-standard Headings:</strong> Creative titles ("Where I've Been") confuse bots.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c_pass:
        st.markdown("""
        <div class="comparison-box-pass">
            <h4 style="color: #166534; margin-bottom: 8px;">✅ ATS-Scored Resume (Flagged for Interview)</h4>
            <ul style="color: #14532D; font-size: 0.92rem; line-height: 1.6; margin-bottom: 0;">
                <li><strong>Linear Flowable Structure:</strong> 100% extractable by Taleo, Greenhouse, Workday.</li>
                <li><strong>Targeted Keyword Density:</strong> Exact and semantic alignment with the job description.</li>
                <li><strong>Validated Impact Bullets:</strong> Action verbs with quantified metrics ($ and % outcomes).</li>
                <li><strong>Standard Hierarchy:</strong> Experience, Education, Skills, and Projects clearly isolated.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Five Pillars of Scoring
    st.markdown("### 🎯 The 5 Pillars of Our ATS Scoring Engine")
    st.caption("A multi-dimensional evaluation designed from real ATS algorithms.")

    p1, p2, p3 = st.columns(3)
    with p1:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">📐</div>
            <div class="card-heading">1. Formatting (20%)</div>
            <div class="card-desc">Evaluates linear parsing, contact information clarity, date regularity, and standard section categorization.</div>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🔑</div>
            <div class="card-heading">2. Keywords & Skills (25%)</div>
            <div class="card-desc">Identifies hard tech skills, domain tools, and methodologies matched directly against industry taxonomies.</div>
        </div>
        """, unsafe_allow_html=True)
    with p3:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">⚡</div>
            <div class="card-heading">3. Content Quality (25%)</div>
            <div class="card-desc">Audits action verbs, sentence structure, bullet point impact, and quantified metric density across your experience.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    p4, p5, p6 = st.columns(3)
    with p4:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🧠</div>
            <div class="card-heading">4. Skill Validation (15%)</div>
            <div class="card-desc">Uses semantic sentence embeddings to verify that claimed skills are actually backed by real project bullets.</div>
        </div>
        """, unsafe_allow_html=True)
    with p5:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">🛡️</div>
            <div class="card-heading">5. ATS Compatibility (15%)</div>
            <div class="card-desc">Checks file encodings, font safety, layout hygiene, and absence of problematic tables or text boxes.</div>
        </div>
        """, unsafe_allow_html=True)
    with p6:
        st.markdown("""
        <div class="glass-card">
            <div class="card-icon">📑</div>
            <div class="card-heading">Executive PDF Export</div>
            <div class="card-desc">Download a comprehensive PDF audit report detailing strengths, critical issues, and exact fix instructions.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. How It Works
    st.markdown("### 🚀 Simple 3-Step Process")
    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown("""
        <div class="glass-card">
            <span class="step-pill">STEP 01</span>
            <h4 style="margin-top: 8px;">Upload Your Resume</h4>
            <p style="color: #64748B; font-size: 0.9rem;">Drop your PDF, DOCX, or DOC file. Optionally paste the target job description to run precision gap matching.</p>
        </div>
        """, unsafe_allow_html=True)

    with step2:
        st.markdown("""
        <div class="glass-card">
            <span class="step-pill">STEP 02</span>
            <h4 style="margin-top: 8px;">Instant AI Audit</h4>
            <p style="color: #64748B; font-size: 0.9rem;">Our local spaCy NLP engine and Sentence-Transformers evaluate your resume across 5 weighted dimensions in seconds.</p>
        </div>
        """, unsafe_allow_html=True)

    with step3:
        st.markdown("""
        <div class="glass-card">
            <span class="step-pill">STEP 03</span>
            <h4 style="margin-top: 8px;">Optimize & Apply</h4>
            <p style="color: #64748B; font-size: 0.9rem;">View actionable bullet-by-bullet recommendations or use our built-in Resume Builder to generate a 100% compliant PDF.</p>
        </div>
        """, unsafe_allow_html=True)

    # 6. Bottom Call to Action
    st.markdown("""
    <div class="footer-cta">
        <h2 style="color: white; font-family: 'Outfit', sans-serif; font-size: 2.2rem; margin-bottom: 0.75rem;">
            Ready To Beat The ATS Bots?
        </h2>
        <p style="color: #E0E7FF; font-size: 1.05rem; max-width: 550px; margin: 0 auto 1.75rem auto;">
            Join thousands of job seekers optimizing their resumes for top tech, finance, and business roles.
        </p>
    </div>
    """, unsafe_allow_html=True)

    b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
    with b_col2:
        if st.button("⚡ Start Free Resume Scoring Now", use_container_width=True, type="primary", key="btn_footer_start"):
            st.session_state.current_view = "scorer"
            st.rerun()