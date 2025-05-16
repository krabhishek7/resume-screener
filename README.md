# AI-Powered Resume Screener

An intelligent system that automatically screens, ranks, and matches candidate resumes with job descriptions using machine learning and NLP techniques.

## Features

- **Resume Parser:** Extract key information from PDF and DOC resumes
- **Job Matching Engine:** Match candidates to job descriptions based on skills, experience, and education
- **Candidate Ranking:** Score and rank candidates for specific job openings
- **HR Analytics Dashboard:** View insights and metrics about your candidate pool
- **Resume Storage:** Securely store and organize candidate information
- **RESTful API:** Integration-ready endpoints for third-party applications

## Tech Stack

- **Backend:** FastAPI, Python
- **ML/NLP:** PyTorch, Transformers, spaCy, scikit-learn
- **Data Storage:** MongoDB
- **Frontend:** HTML/CSS/JS with Jinja2 templates
- **Document Processing:** PyPDF2, python-docx, textract

## Project Structure

```
resume-screener/
├── app/                   # Main application directory
│   ├── api/               # API endpoints
│   ├── core/              # Core application components
│   ├── db/                # Database models and connections
│   ├── models/            # ML models and logic
│   ├── parsers/           # Resume parsing logic
│   ├── schemas/           # Pydantic schemas for validation
│   ├── services/          # Business logic services
│   ├── static/            # Static assets
│   └── templates/         # Jinja2 HTML templates
├── tests/                 # Test files
├── data/                  # Data storage (gitignored)
│   ├── resumes/           # Uploaded resumes storage
│   └── models/            # Trained ML models
├── scripts/               # Utility scripts
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── main.py                # Application entry point
├── README.md              # Project documentation
└── requirements.txt       # Project dependencies
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/resume-screener.git
cd resume-screener
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install spaCy language model:
```bash
python -m spacy download en_core_web_md
```

5. Create .env file (see .env.example for required variables)

6. Run the application:
```bash
python main.py
```

## API Documentation

Once the server is running, visit http://localhost:8000/docs for the interactive API documentation.

## License

MIT 



            ┌─────────────┐
            │   Upload    │
            │ (PDF/DOCX)  │
            └─────┬───────┘
                  ▼
         ┌────────────────┐
         │ Resume Parser  │  ← spaCy/NLP + PDF Extract
         └─────┬──────────┘
               ▼
     ┌──────────────────────┐
     │ Structured Candidate │
     │      Profile         │
     └─────┬────────────────┘
           ▼
 ┌────────────────────────────┐
 │ Job Description Matcher    │  ← BERT Embeddings / TF-IDF
 └────────┬───────────────────┘
          ▼
 ┌────────────────────────────┐
 │ Candidate Scoring & Ranker │  ← ML or heuristic-based
 └────────┬───────────────────┘
          ▼
 ┌────────────────────────────┐
 │   Streamlit Dashboard      │  ← UI for recruiters
 └────────────────────────────┘
