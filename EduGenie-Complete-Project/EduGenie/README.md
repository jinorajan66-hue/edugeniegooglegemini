# EduGenie: Google Gemini Powered Learning Assistant

EduGenie is a lightweight educational web application based on the supplied project
documentation. The documented architecture contains a FastAPI backend, an HTML/CSS
frontend, Gemini-powered Q&A, quiz generation, summarization, learning recommendations,
and a local LaMini-Flan-T5 explanation option.

## What is included

- Ask educational questions
- Explain a topic in beginner-friendly language
- Generate exactly 3 MCQs with 4 options each
- Summarize educational text
- Generate a Beginner -> Intermediate -> Advanced learning path
- Interactive quiz answer checking in the browser
- Health endpoint and automated API tests
- Optional local `MBZUAI/LaMini-Flan-T5-783M` explanation model
- Environment-based Gemini configuration

## Project structure

```text
EduGenie/
├── main.py
├── config.py
├── schemas.py
├── utils.py
├── ai_service.py
├── explanation_module.py
├── qna.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── requirements-local.txt
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
└── tests/
    └── test_app.py
```

## 1. Prerequisites

- Python 3.10 or newer
- VS Code
- Internet connection for Gemini API
- A Gemini API key for live AI features

The original document specifies Python 3.10+, FastAPI, HTML/CSS, Uvicorn,
Jinja2, Gemini, and the LaMini-Flan-T5 model.

## 2. Open the project in VS Code

Open the `EduGenie` folder in VS Code.

Then open **Terminal -> New Terminal**.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## 3. Configure Gemini

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

with your real key.

Google AI Studio provides Gemini API keys. Keep `.env` private and never commit
it to Git.

## 4. Run the application

```powershell
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI API documentation is also available at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 5. Test every feature

### Ask a question

Try:

```text
Which is the largest ocean?
```

### Explain a topic

Try:

```text
Pythagoras theorem
```

### Generate a quiz

Paste:

```text
The Pythagorean theorem states that in a right-angled triangle,
the square of the hypotenuse is equal to the sum of the squares
of the other two sides.
```

EduGenie returns 3 MCQs with 4 options each.

### Summarize

Paste any long educational paragraph.

### Learning recommendations

Try:

```text
SQL
```

The response is organized into Beginner, Intermediate, and Advanced levels.

## 6. Run automated tests

With the virtual environment activated:

```powershell
pytest
```

The tests mock the AI layer, so they do not consume Gemini API quota.

## 7. Optional: enable the local LaMini explanation model

The supplied documentation describes `LaMini-Flan-T5-783M` as the local
concept-explanation model. Because this model adds a large download and local
runtime dependencies, the base project keeps it disabled by default.

Install the optional dependencies:

```powershell
pip install -r requirements-local.txt
```

Then set:

```text
ENABLE_LOCAL_EXPLANATION=true
```

in `.env`.

On the first explanation request, Transformers downloads the model from Hugging
Face. If local loading fails, EduGenie falls back to Gemini so the application
can remain usable.

## 8. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web interface |
| GET | `/health` | Application status |
| POST | `/qa` | Question answering |
| POST | `/explain` | Topic explanation |
| POST | `/quiz` | 3-question MCQ generation |
| POST | `/summarize` | Text summarization |
| POST | `/learn/recommendations` | Learning path generation |

Example:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/qa `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"question":"Which is the largest ocean?"}'
```

## Troubleshooting

### `GEMINI_API_KEY is not configured`

Make sure `.env` exists in the project root and contains a valid key.

Restart Uvicorn after changing `.env`.

### PowerShell says scripts are disabled

Use Command Prompt, or allow activation for the current PowerShell user if
that is appropriate for your machine.

### `ModuleNotFoundError`

Confirm the virtual environment is activated and run:

```powershell
pip install -r requirements.txt
```

### Local model is slow or fails

Set:

```text
ENABLE_LOCAL_EXPLANATION=false
```

The application will use Gemini for explanations.

### Port 8000 is busy

Run:

```powershell
uvicorn main:app --reload --port 8001
```

Then open `http://127.0.0.1:8001`.

## Architecture

```text
Browser
   |
   v
FastAPI / main.py
   |
   +--> /qa ----------------------> qna.py
   |
   +--> /explain -----------------> explanation_module.py
   |                                  |
   |                                  +--> LaMini (optional)
   |                                  +--> Gemini fallback
   |
   +--> /quiz --------------------> quiz_module.py
   |                                  |
   |                                  +--> Gemini structured JSON
   |
   +--> /summarize ---------------> summary_module.py
   |
   +--> /learn/recommendations ---> learning_path.py
                                      |
                                      +--> Gemini structured JSON
```

## Design decisions made to keep the documented project working

The supplied document names Gemini 1.5 Pro. That model choice is kept as part of
the project's historical architecture, but the code does not hard-code that
retired/legacy model. The active model is configurable through `GEMINI_MODEL`.
The default is `gemini-2.5-flash`, which can be changed without editing source code.

The original document also places LaMini in the explanation path. This project
keeps that capability while making it opt-in, because downloading and loading a
large local model on every developer machine is not a good default for a
lightweight FastAPI application.

Structured Gemini output is used for quizzes and learning paths so the frontend
receives predictable JSON instead of having to guess how to parse free-form text.
