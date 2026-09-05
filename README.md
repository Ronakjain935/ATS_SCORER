# ATS Resume Scorer & Analyzer 🎯📄

An intelligent, AI-powered Application Tracking System (ATS) resume scorer and analyzer built with **FastAPI** and **Streamlit**. Evaluates resumes against job descriptions, provides comprehensive match analytics, detects strengths and missing skills, and suggests actionable improvements.

---

## 🌟 Key Features

- **ATS Scoring Engine**: Computes overall match score, semantic similarity, and keyword coverage.
- **Deep Resume Analysis**: Extracts key sections, contact information, education, experience, and validated skills.
- **Job Description Comparison**: Side-by-side gap analysis identifying matched keywords, missing competencies, and experience alignment.
- **Actionable Feedback & Recommendations**: AI-driven suggestions powered by Groq and SentenceTransformers to boost interview chances.
- **Modern Interactive Dashboard**: Premium Streamlit UI with visual score gauges, breakdown charts, and detailed feedback tabs.
- **User History & Cloud Integration**: Supabase authentication and historical score tracking.

---

## 🏗️ Architecture

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (REST API) with SpaCy, SentenceTransformers, and Groq API.
- **Frontend**: [Streamlit](https://streamlit.io/) with custom styling and modular UI components.
- **Database / Auth**: [Supabase](https://supabase.com/) for user authentication and analysis history.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Ronakjain935/ATS_SCORER.git
cd ATS_SCORER
```

### 2. Set Up a Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and configure your API keys:
```bash
copy backend\.env.example backend\.env   # Windows
# or
cp backend/.env.example backend/.env      # Linux/macOS
```

Fill in your credentials in `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_ANON_KEY=your_supabase_anon_key
AUTH_REDIRECTED_URL=http://localhost:8501
```

### 5. Download NLP Models (Optional / Fallback provided)
```bash
python -m spacy download en_core_web_sm
```

---

## 💻 Running the Application

### Option A: One-Click Run (Windows)
Double-click `run_app.bat` or run:
```bat
run_app.bat
```

### Option B: Run Services Separately

**Start Backend (FastAPI):**
```bash
uvicorn backend.main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

**Start Frontend (Streamlit):**
```bash
streamlit run frontend/app.py --server.port 8501
```
- Web Application: [http://localhost:8501](http://localhost:8501)

---

## 📂 Project Structure

```
ATS_SCORER/
├── backend/                  # FastAPI Application
│   ├── api/                  # API endpoints and routers
│   ├── core/                 # App configurations and constants
│   ├── models/               # Pydantic schemas and database models
│   ├── services/             # Scoring algorithms, NLP extraction, embedders
│   ├── templates/            # HTML templates for reports
│   └── main.py               # FastAPI entrypoint
├── frontend/                 # Streamlit Web Application
│   ├── .streamlit/           # Streamlit configs & styles
│   ├── components/           # Reusable UI widgets and score cards
│   ├── services/             # API client & Supabase auth
│   ├── views/                # Multi-page views (landing, scorer, history, resources)
│   └── app.py                # Streamlit entrypoint
├── run_app.bat               # Windows launcher script
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 📄 License
This project is licensed under the MIT License.
