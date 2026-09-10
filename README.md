# 🎯 ATS Resume Scorer & Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/spaCy-3.7%2B-09A3D5?style=for-the-badge&logo=spacy&logoColor=white" alt="spaCy" />
  <img src="https://img.shields.io/badge/HuggingFace-SentenceTransformers-yellow?style=for-the-badge&logo=huggingface&logoColor=white" alt="HuggingFace" />
  <img src="https://img.shields.io/badge/ReportLab-PDF%20Generation-red?style=for-the-badge" alt="ReportLab" />
  <img src="https://img.shields.io/badge/Supabase-Auth%20%26%20DB-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Groq-LLM%20Inference-F55036?style=for-the-badge" alt="Groq" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

An enterprise-grade, AI-driven **Applicant Tracking System (ATS) Resume Scorer, Optimizer, and Resume Builder**. This application empowers job seekers and recruiters to evaluate resumes against target job descriptions using Natural Language Processing (NLP), semantic embeddings, and LLM-powered recommendations, and generate 100% ATS-compliant resumes in seconds.

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

Modern companies filter out up to 75% of resumes before human review using Automated Applicant Tracking Systems (ATS). The **ATS Resume Scorer & Analyzer** bridges this gap by dissecting resume documents, testing them against industry ATS criteria, computing semantic similarity against job requirements, providing tailored improvements, and offering a built-in **ATS-Friendly Resume Builder** to generate pre-optimized resumes that pass every parser.

---

## ✨ Key Features

### 1. 📝 ATS-Friendly Resume Builder & Generator (New!)
- **7-Tab Interactive Form**: Enter personal details, professional summary, categorized skills, work experience, projects, education, certifications, and achievements.
- **✨ 1-Click Sample Profile Preloader**: Immediately populate all fields with a realistic, high-scoring tech profile for testing and inspiration.
- **Strict Single-Column ATS Standards**: Built with Python's `reportlab` engine adhering strictly to ATS typography, margin, and layout hygiene guidelines.
- **Customizable Color Accents**: Choose between *Modern Navy, Classic Charcoal, Slate Blue, or Forest Green*.
- **Multi-Format Export**: Download as a printable, ATS-optimized PDF or export as clean plain text (`.txt`) for copy-pasting into job portals.
- **⚡ Direct ATS Scorer Integration**: 1-click button transfering your newly generated resume into the ATS Scorer to test and verify its compatibility score on the spot.

### 2. Multi-Format Resume Parsing
- Extracts raw text, structured sections, and contact metadata from `.pdf`, `.docx`, and `.doc` files (up to 5 MB).
- Resilient PDF text extraction using `pdfplumber` / `pypdf` with encoding normalization and multi-engine fallbacks.

### 3. Comprehensive 5-Component ATS Scoring
Calculates a weighted, 100-point overall score across five key dimensions:
- **Formatting & Structure (20%)**: Section header detection, single-column reading order, contact details completeness.
- **Keyword Coverage (25%)**: Industry keywords and job-specific terminology frequency.
- **Content & Impact (25%)**: Action verbs, measurable metrics, quantifiable achievements, and sentence structure.
- **Skill Validation (15%)**: Distinguishes between keyword-stuffed claims vs. skills backed by contextual evidence in project/experience bullets.
- **ATS Compatibility (15%)**: Readability index, file parsing cleanliness, and absence of ATS-unfriendly artifacts.

### 4. Deep Job Description (JD) Gap Analysis
- **Semantic Similarity (40% JD weight)**: Computed via `SentenceTransformer` (`all-MiniLM-L6-v2`) cosine embeddings.
- **Keyword Match Rate (60% JD weight)**: Extracts high-value requirements and flags:
  - Matched keywords
  - Missing keywords & competencies
  - Skill gaps prioritized by importance

### 5. Resilient Offline NLP Fallback Engine
- **Hybrid AI Pipeline**: Blends **Groq Cloud LLM** inference for low-latency recommendations with a robust **local regex and NLP parser**.
- **Zero 500 Crashes**: If Groq credentials are unset, expired, or offline, the system automatically falls back to its built-in catalog of ~150+ technical skills and action verbs without interrupting analysis.

### 6. PDF Audit Report Export
- Compiles modular HTML report templates (`summary.html`, `jd_comparison.html`, `action_items.html`, `quick_actions.html`).
- Converts reports into downloadable, print-ready PDF audit documents.

### 7. Cloud Persistence & User Authentication
- **Supabase Authentication**: Secure user sign-up, login, and session tokens.
- **Guest Mode**: Full scoring and report generation available locally without requiring sign-in.
- **Scan History**: Retains past resume evaluations, historical score trends, and archived PDF downloads for authenticated users.

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
|  |   Resume Parser     |   |   spaCy NLP         |   | SentenceTransformer |   |  Groq / Local   |  |
|  | (pdfplumber/docx)   |   | (en_core_web_md/sm) |   | (all-MiniLM-L6-v2)  |   | Fallback NLP    |  |
|  +----------+----------+   +----------+----------+   +----------+----------+   +--------+--------+  |
|             |                         |                         |                       |           |
|             +-------------------------+------------+------------+-----------------------+           |
|                                                    v                                                |
|                                      +---------------------------+                                  |
|                                      |   ATS Scoring Engine      |                                  |
|                                      | (5-Component Calculation) |                                  |
|                                      +-------------+-------------+                                  |
|                                                    |                                                |
|                     +------------------------------+------------------------------+                 |
|                     v                                                             v                 |
|         +-----------------------+                                     +-----------------------+     |
|         |  ReportLab & xhtml2pdf|                                     | Supabase Cloud DB     |     |
|         |  (PDF Audit & Resume) |                                     | (History & Auth)      |     |
|         +-----------------------+                                     +-----------------------+     |
+-----------------------------------------------------------------------------------------------------+
```

---

## ⚖️ Scoring Engine & Methodology

| Component | Weight | Criteria Evaluated |
| :--- | :---: | :--- |
| **Formatting** | 20% | Clear section headers (`Experience`, `Education`, `Skills`), contact presence, single-column parsing fidelity |
| **Keywords** | 25% | Industry terms, skill density, technical vocabulary, alignment with industry norms |
| **Content** | 25% | Presence of metric-driven accomplishments (`%`, `$`, numbers), action verbs (`Spearheaded`, `Engineered`) |
| **Skill Validation** | 15% | Semantic link between listed skills and project/work bullet points (discourages keyword stuffing) |
| **ATS Compatibility** | 15% | Plain text extractability, low risk of character encoding distortion, clean font structures |

---

## 🧰 Technology Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **Frontend Dashboard**: [Streamlit](https://streamlit.io/)
- **NLP & Linguistics**: [spaCy](https://spacy.io/) (`en_core_web_md` / `en_core_web_sm`)
- **Semantic Embeddings**: [SentenceTransformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`)
- **Document Generation**: [ReportLab](https://www.reportlab.com/) & [xhtml2pdf](https://xhtml2pdf.readthedocs.io/)
- **Document Parsers**: `pdfplumber`, `PyPDF2`, `python-docx`
- **LLM Engine**: [Groq](https://groq.com/) API client with resilient local fallback parser
- **Database & Auth**: [Supabase](https://supabase.com/) (PostgreSQL + Row Level Security)

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
│   │   ├── groq_parser.py            # LLM prompts & offline regex/NLP fallback parser
│   │   ├── jd_matcher.py             # Keyword gap analysis & semantic similarity
│   │   ├── pdf_export.py             # HTML to PDF audit report exporter
│   │   ├── recommendation_engine.py  # Prioritized improvement roadmap generator
│   │   ├── report_generator.py       # Jinja2 report rendering
│   │   ├── resume_analyzer.py        # Full orchestration pipeline
│   │   └── resume_parser.py          # Document text extraction (.pdf, .docx, .doc)
│   ├── templates/                    # Jinja2 HTML templates for PDF reports
│   └── main.py                       # FastAPI application entrypoint & lifespan
│
├── frontend/
│   ├── .streamlit/
│   │   └── config.toml               # Streamlit server & theme configurations
│   ├── components/                   # Modular UI components
│   │   ├── dashboard.py              # Visual summary dashboard
│   │   ├── detailed_feedback.py      # Tabulated section feedback
│   │   ├── jd_comparison.py          # Side-by-side JD comparison widget
│   │   └── recommendations.py        # Tailored improvement recommendations
│   ├── services/
│   │   ├── api_client.py             # HTTP client communicating with FastAPI backend
│   │   ├── resume_generator.py       # ATS-compliant PDF & Plain-Text Resume Builder engine
│   │   └── supabase_client.py        # Frontend Supabase authentication handling
│   ├── views/                        # Streamlit pages
│   │   ├── builder.py                # ATS-Friendly Resume Builder panel
│   │   ├── history.py                # Scan history and report downloads
│   │   ├── landing.py                # Hero section & feature tour
│   │   ├── resources.py              # ATS resume building guides & resources
│   │   └── scorer.py                 # Core resume upload & evaluation view
│   ├── app.py                        # Streamlit main entrypoint
│   └── streamlite_app.py             # Complete modular application view router
│
├── .env.example                      # Sample environment variables
├── requirements.txt                  # Python dependencies
├── run_app.bat                       # 1-Click launcher for Backend + Frontend
└── main.py                           # Root runner script
```

---

## ⚙️ Prerequisites

Ensure you have the following installed:
- **Python 3.10 or higher** (Python 3.11 recommended)
- **Git**
- **pip** package manager

Optional third-party accounts:
- [Groq Cloud API Key](https://console.groq.com/) *(Optional: local NLP parser active by default)*
- [Supabase Account](https://supabase.com/) *(Optional: guest mode enabled by default)*

---

## 🚀 Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/Ronakjain935/ATS_SCORER.git
cd ATS_SCORER
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
# Optional higher accuracy model:
python -m spacy download en_core_web_md
```

---

## 🔑 Environment Configuration

Create a `.env` file in the project root:

```env
# Groq API Key (Optional - application runs offline NLP fallback if not provided)
GROQ_API_KEY=your_groq_api_key_here

# Supabase Credentials (Optional - local Guest Mode enabled by default)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Hugging Face Token (Optional)
HF_TOKEN=your_huggingface_token_here
```

---

## 🏃 Running the Application

### Method 1: 1-Click Launcher (Windows)
Double-click `run_app.bat` or run:
```cmd
run_app.bat
```
This automatically launches both the FastAPI backend and Streamlit frontend in parallel.

---

### Method 2: Manual Execution

#### Terminal 1 — Start FastAPI Backend:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

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

The Streamlit application includes five dedicated views:
1. **🏠 Home**: Overview of system capabilities, features, and quick links.
2. **🎯 ATS Scorer**: Upload `.pdf`/`.docx` resumes, compare against job descriptions, view multi-dimensional scores, radar charts, and suggestions.
3. **📝 Resume Builder**: Interactive 7-tab resume builder generating clean, single-column ATS-compliant resumes with PDF & text export, plus 1-click ATS score testing.
4. **📊 History**: Track past analyses, compare score improvements across iterations, and re-download PDF audits.
5. **📚 Resources**: Actionable ATS guidelines, resume formatting best practices, and action-verb cheat sheets.

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
