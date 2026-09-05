# 🎯 ATS Resume Scorer & Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/spaCy-3.7%2B-09A3D5?style=for-the-badge&logo=spacy&logoColor=white" alt="spaCy" />
  <img src="https://img.shields.io/badge/HuggingFace-SentenceTransformers-yellow?style=for-the-badge&logo=huggingface&logoColor=white" alt="HuggingFace" />
  <img src="https://img.shields.io/badge/Supabase-Auth%20%26%20DB-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Groq-LLM%20Inference-F55036?style=for-the-badge" alt="Groq" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

An enterprise-grade, AI-driven **Applicant Tracking System (ATS) Resume Scorer and Optimizer**. This application empowers job seekers and recruiters to evaluate resumes against target job descriptions using cutting-edge Natural Language Processing (NLP), semantic embeddings, and LLM-powered recommendations.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Scoring Engine & Methodology](#-scoring-engine--methodology)
- [Technology Stack](#-technology-stack)
- [Directory Structure](#-directory-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Environment Configuration](#-environment-configuration)
- [Running the Application](#-running-the-application)
- [REST API Reference](#-rest-api-reference)
- [Frontend Navigation](#-frontend-navigation)
- [License](#-license)

---

## 🔍 Overview

Modern companies filter out up to 75% of resumes before human review using Automated Applicant Tracking Systems (ATS). The **ATS Resume Scorer & Analyzer** bridges this gap by dissecting resume documents, testing them against industry ATS criteria, computing semantic similarity against job requirements, and providing tailored improvements.

---

## ✨ Key Features

### 1. Multi-Format Resume Parsing
- Extracts raw text, structured sections, and contact metadata from `.pdf`, `.docx`, and `.doc` files (up to 5 MB).
- Resilient PDF text extraction using `pdfplumber` / `pypdf` with encoding normalization.

### 2. Comprehensive 5-Component ATS Scoring
Calculates a weighted, 100-point overall score across five key dimensions:
- **Formatting & Structure (20%)**: Section header detection, layout hygiene, contact details completeness.
- **Keyword Coverage (25%)**: Industry keywords and job-specific terminology frequency.
- **Content & Impact (25%)**: Action verbs, measurable metrics, quantifiable achievements, and sentence structure.
- **Skill Validation (15%)**: Distinguishes between keyword-stuffed claims vs. skills backed by contextual evidence in project/experience bullets.
- **ATS Compatibility (15%)**: Readability index, file parsing cleanliness, and absence of ATS-unfriendly artifacts.

### 3. Deep Job Description (JD) Gap Analysis
- **Semantic Similarity (40% JD weight)**: Computed via `SentenceTransformer` (`all-MiniLM-L6-v2`) cosine embeddings.
- **Keyword Match Rate (60% JD weight)**: Extracts high-value requirements and flags:
  - Matched keywords
  - Missing keywords & competencies
  - Skill gaps prioritized by importance

### 4. AI-Powered Actionable Recommendations
- Powered by **Groq Cloud LLM** inference for low-latency, high-precision recommendations.
- Specific, context-aware rewriting suggestions for resume bullet points.
- Instant quick-fix action checklists for immediate score improvements.

### 5. PDF Audit Report Export
- Compiles modular HTML report templates (`summary.html`, `jd_comparison.html`, `action_items.html`, `quick_actions.html`).
- Converts reports into downloadable, print-ready PDF audit documents.

### 6. Cloud Persistence & User Authentication
- **Supabase Authentication**: Secure user sign-up, login, and session tokens.
- **Scan History**: Retains past resume evaluations, historical score trends, and archived PDF downloads.

---

## 🏛️ System Architecture

```
                                  +---------------------------------------+
                                  |         User Web Browser              |
                                  |    (Streamlit Modern UI @ :8501)       |
                                  +-------------------+-------------------+
                                                      |
                                                      | HTTP / REST Calls
                                                      v
+-----------------------------------------------------------------------------------------------------+
|                                      FastAPI Backend (@ :8000)                                      |
|                                                                                                     |
|  +---------------------+   +---------------------+   +---------------------+   +-----------------+  |
|  |   Resume Parser     |   |   spaCy NLP         |   | SentenceTransformer |   |  Groq LLM       |  |
|  | (pdfplumber/docx)   |   | (en_core_web_md/sm) |   | (all-MiniLM-L6-v2)  |   | (AI Insights)   |  |
|  +----------+----------+   +----------+----------+   +----------+----------+   +--------+--------+  |
|             |                         |                         |                       |           |
|             +-------------------------+------------+------------+-----------------------+           |
|                                                    v                                                |
|                                      +---------------------------+                                  |
|                                      |   ATS Scoring Engine      |                                  |
|                                      | (5-Component Calculation) |                                  |
|                                      +-------------+-------------+                                  |
|                                                    |                                                |
|                                                    v                                                |
|                                      +---------------------------+                                  |
|                                      |  PDF Export & Generator   |                                  |
|                                      | (Jinja2 Templates -> PDF) |                                  |
|                                      +---------------------------+                                  |
+----------------------------------------------------+------------------------------------------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      |     Supabase Cloud          |
                                      |  * Auth (JWT Validation)    |
                                      |  * History & Scan Storage   |
                                      +-----------------------------+
```

---

## 📊 Scoring Engine & Methodology

| Component | Default Weight | Key Signals Evaluated |
| :--- | :---: | :--- |
| **Formatting** | **20%** | Standard section headers, email/phone presence, clean structure |
| **Keywords** | **25%** | Domain keywords, technical proficiencies, role-specific vocabulary |
| **Content** | **25%** | Active voice, power verbs, quantified metrics (`%`, `$`, numbers) |
| **Skill Validation** | **15%** | Contextual proof for claimed skills within work experience |
| **ATS Compatibility** | **15%** | Standard fonts, readable formatting, absence of tables/images |

When a **Job Description** is provided, the system computes an aligned **JD Match Percentage**:
$$\text{JD Match Score} = (0.60 \times \text{Keyword Match}) + (0.40 \times \text{Semantic Cosine Similarity})$$

---

## 💻 Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous REST API)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Template Engine**: [Jinja2](https://palletsprojects.com/p/jinja/)
- **PDF Generation**: `weasyprint` / `xhtml2pdf`

### Machine Learning & NLP
- **Core NLP**: [spaCy](https://spacy.io/) (`en_core_web_md` / `en_core_web_sm`)
- **Embeddings**: [SentenceTransformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
- **LLM Engine**: [Groq](https://groq.com/) API client for fast inference

### Frontend
- **Framework**: [Streamlit](https://streamlit.io/)
- **Styling**: Custom CSS design system with glassmorphism effects and responsive charts

### Cloud & Database
- **Auth & Storage**: [Supabase](https://supabase.com/) Python Client

---

## 📁 Directory Structure

```text
ATS_SCORER/
├── backend/
│   ├── api/
│   │   ├── auth.py                   # Supabase JWT authentication dependency
│   │   └── routes.py                 # REST API endpoints (/analyze, /history, /generate-pdf)
│   ├── core/
│   │   └── config.py                 # Application settings, model names, scoring weights
│   ├── database/
│   │   ├── supabase.py               # Supabase client initialization
│   │   └── supabase_db.py            # User history queries (CRUD)
│   ├── models/
│   │   └── schemas.py                # Pydantic request & response schemas
│   ├── services/
│   │   ├── ats_scorer.py             # 5-factor scoring engine
│   │   ├── embedder_fallback.py      # Fallback vector embedder when GPU/Torch unavailable
│   │   ├── feedback_engine.py        # Grammar, readability, and content evaluation
│   │   ├── groq_parser.py            # LLM prompts for resume parsing & suggestions
│   │   ├── jd_matcher.py             # Keyword gap analysis & semantic similarity
│   │   ├── pdf_export.py             # HTML to PDF conversion service
│   │   ├── recommendation_engine.py  # Prioritized improvement roadmap generator
│   │   ├── report_generator.py       # Jinja2 report rendering
│   │   ├── resume_analyzer.py        # Full orchestration pipeline
│   │   └── resume_parser.py          # Document text extraction (.pdf, .docx, .doc)
│   ├── templates/                    # Jinja2 HTML templates for PDF reports
│   │   ├── action_items.html
│   │   ├── jd_comparison.html
│   │   ├── quick_actions.html
│   │   └── summary.html
│   ├── utils/
│   │   ├── file_utils.py             # File helpers and default fallbacks
│   │   └── matching.py               # String matching and fuzzy comparisons
│   └── main.py                       # FastAPI application entrypoint & lifespan
│
├── frontend/
│   ├── .streamlit/
│   │   ├── assets/
│   │   │   └── styles.css            # Custom CSS styling & UI enhancements
│   │   └── config.toml               # Streamlit server & theme configurations
│   ├── components/                   # Modular UI components
│   │   ├── action_items.py           # Priority action items card
│   │   ├── dashboard.py              # Visual summary dashboard
│   │   ├── detailed_feedback.py      # Tabulated section feedback
│   │   ├── jd_comparison.py          # Side-by-side JD comparison widget
│   │   ├── recommendations.py        # Tailored improvement recommendations
│   │   ├── score_display.py          # Gauge charts & overall score badges
│   │   ├── skill_validation.py       # Validated vs unvalidated skills breakdown
│   │   └── strengths_issues.py       # Strengths and issues cards
│   ├── services/
│   │   ├── api_client.py             # HTTP client communicating with FastAPI backend
│   │   └── supabase_client.py        # Frontend Supabase authentication handling
│   ├── views/                        # Streamlit pages
│   │   ├── history.py                # Scan history and report downloads
│   │   ├── landing.py                # Hero section & feature tour
│   │   ├── resources.py              # ATS resume building guides & resources
│   │   └── scorer.py                 # Core resume upload & evaluation view
│   ├── app.py                        # Streamlit main entrypoint
│   └── streamlite_app.py             # Standalone fallback interface
│
├── .gitignore                        # Git exclusion rules
├── main.py                           # Root runner script
├── pyproject.toml                    # Project package metadata
├── requirements.txt                  # Python dependencies
├── run_app.bat                       # Windows one-click launcher
└── README.md                         # Project documentation
```

---

## ⚙️ Prerequisites

- **Python**: Version `3.10` or higher
- **Git** installed
- **API Keys**:
  - [Groq Cloud API Key](https://console.groq.com/)
  - [Supabase Project URL & Anon Key](https://supabase.com/)

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Ronakjain935/ATS_SCORER.git
cd ATS_SCORER
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download spaCy Language Models
```bash
python -m spacy download en_core_web_md
# Fallback model (optional but recommended)
python -m spacy download en_core_web_sm
```

---

## 🔑 Environment Configuration

Create a `.env` file in the `backend/` directory by copying the provided example:

```bash
# Windows
copy backend\.env.example backend\.env

# macOS / Linux
cp backend/.env.example backend/.env
```

Open `backend/.env` and specify your credentials:

```env
# Groq API Key for AI parser and recommendations
GROQ_API_KEY=gsk_your_groq_api_key_here

# Supabase Project Configurations
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Frontend Redirect URL
AUTH_REDIRECTED_URL=http://localhost:8501

# Optional: Override embedding model
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

---

## 🚀 Running the Application

### Method 1: One-Click Launcher (Windows)
Double-click `run_app.bat` or execute in PowerShell:
```cmd
run_app.bat
```
This automatically spins up both the FastAPI backend and Streamlit frontend in separate console windows.

---

### Method 2: Manual Execution

#### Terminal 1 — Start FastAPI Backend:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Redoc Alternative: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Terminal 2 — Start Streamlit Frontend:
```bash
streamlit run frontend/app.py --server.port 8501
```
- Web Application: [http://localhost:8501](http://localhost:8501)

---

## 📡 REST API Reference

All backend routes are accessible under `/api/v1`.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/health` | Verifies service status and loaded ML/NLP models | No |
| `POST` | `/api/v1/analyze-resume` | Uploads and analyzes resume against optional job description | Optional |
| `POST` | `/api/v1/generate-pdf` | Generates a downloadable PDF report from analysis results | Optional |
| `GET` | `/api/v1/history` | Retrieves authenticated user's previous resume scans | Yes (JWT) |
| `DELETE` | `/api/v1/history/{id}` | Deletes a specific scan record from user's history | Yes (JWT) |
| `GET` | `/api/v1/history/{id}/pdf` | Downloads stored PDF report for an existing analysis ID | Yes (JWT) |

---

## 🖥️ Frontend Navigation

The Streamlit interface offers four dedicated views:
1. **🏠 Landing**: Overview of system capabilities, features, and user authentication portal.
2. **📊 Resume Scorer**: Upload `.pdf`/`.docx` resumes, paste job descriptions, and view live score cards, radar charts, and recommendations.
3. **🕒 History**: Track past analyses, compare score improvements across iterations, and re-download PDF audits.
4. **📚 Resources**: Actionable ATS tips, resume formatting best practices, and high-impact action verb cheat sheets.

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m "feat: Add AmazingFeature"`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.
