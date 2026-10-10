# AI Mock Interview

A responsive Flask and vanilla JavaScript application for resume-informed technical interview practice. Upload a PDF or DOCX, select a domain, answer five multiple-choice and five theoretical questions, then receive an explainable 30-point report from Gemini.

## Features

- Resume parsing with PDF and DOCX signature, extension, size, and extracted-text checks. Scanned PDFs are identified when no selectable text can be extracted; OCR is not included.
- Structured resume profile analysis and domain-aware question generation across six technical domains.
- Exactly five MCQs and five open-ended questions. MCQ answer keys and theory rubrics stay in a server-encrypted token and are excluded from generated question JSON sent to the browser.
- Deterministic backend MCQ marking and rubric-based Gemini feedback for theory answers.
- Responsive interview flow with navigation, answer persistence in sessionStorage, progress, Web Speech API input when supported, and SpeechSynthesis question narration.
- Detailed report, question review, reference answers, print-to-PDF, and practice-again flow.
- Same-origin Flask API and frontend; no database or permanent resume storage.

## Stack and architecture

- Python 3.12, Flask, Google Gen AI SDK, pypdf, python-docx, cryptography.
- HTML5, CSS, and plain JavaScript. No frontend build step.
- `app.py` exports the Flask WSGI application for Vercel's zero-configuration Flask discovery. `backend/` contains API and service modules. Static assets and template are included in the Flask function bundle and served same-origin.
- No Vercel configuration file is needed for the recognized Flask entrypoint. Vercel's current Python runtime supports Flask and Python 3.12; see [Flask on Vercel](https://vercel.com/docs/frameworks/backend/flask) and [Python Runtime](https://vercel.com/docs/functions/runtimes/python).

## Project structure

```text
app.py
backend/
  __init__.py       Flask factory, page route, security headers
  config.py         Environment configuration
  routes.py         Health, resume, interview and evaluation endpoints
  resume_service.py PDF/DOCX validation and extraction
  gemini_service.py Google Gen AI JSON requests and bounded retry
  question_service.py schema checks and domain fallback set
  evaluation_service.py deterministic score and report creation
  security.py       Fernet authenticated encrypted state tokens
templates/index.html
static/css/styles.css
static/js/app.js
tests/
requirements.txt
.env.example
.python-version
```

## Local setup

Use Python 3.12. Create a virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Copy `.env.example` to `.env`, then put your Gemini API key and a unique random secret in `.env`. The app loads `.env` automatically for local development. Keep `.env` private; it is ignored by Git. Example for setting variables temporarily in PowerShell instead:

```powershell
$env:GEMINI_API_KEY = "your-key"
$env:GEMINI_MODEL = "gemini-3.8-flash"
$env:FLASK_SECRET_KEY = "use-a-long-random-value"
python app.py
```

Open `http://127.0.0.1:5000`. Health check: `http://127.0.0.1:5000/api/health`.

### Environment variables

| Name | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Yes for profile and theory evaluation | Google AI Studio / Gemini API credential; never sent to the browser |
| `GEMINI_MODEL` | No | Model name; defaults to `gemini-3.8-flash` |
| `FLASK_SECRET_KEY` | Yes in production | Secret used to derive the Fernet encryption key for opaque interview tokens |
| `MAX_UPLOAD_BYTES` | No | Upload cap; defaults to 4 MiB to fit under Vercel's 4.5 MB function request limit |

The app can generate domain-specific fallback questions if question generation is unavailable. Resume analysis and theory evaluation still require Gemini. Configure a Gemini API key and confirm model access before a live session.

## Workflow and scoring

1. The backend validates and extracts resume text in memory, then asks Gemini for a structured profile.
2. The user selects one of six technical domains. Gemini generates five resume-informed MCQs and five theoretical questions. Invalid/failed generation gets domain-specific fallback questions; the interface labels this fallback so it does not claim full personalization.
3. The interview token contains the question set, answer key, rubric, and profile in authenticated encryption. The browser stores the opaque token and candidate answers in `sessionStorage` for up to eight hours. The original file and raw extracted resume text are not retained by the application.
4. The backend compares MCQs directly and asks Gemini to evaluate each theoretical answer from 0–5.

MCQs are worth 1 point each (5 total); theory answers are worth up to 5 points each (25 total). Raw maximum is 30. Percentage = raw score / 30 × 100. Final score = round(percentage / 10, 1), out of 10. Score categories are practice feedback, not a hiring decision.

## Tests

Install dependencies, then run:

```powershell
python -m pytest -q
```

Tests mock Gemini calls and do not require a live key or paid API access.

## Vercel deployment

1. Commit this project to a GitHub repository. `.env` is ignored; do not commit credentials or resumes.
2. Import the repository in Vercel. Keep the root directory at the repository root and use the default Python/Flask detection. This project intentionally has no `vercel.json` rewrite because the Flask app owns both page and API routes.
3. In Project Settings → Environment Variables, add `GEMINI_API_KEY`, `FLASK_SECRET_KEY`, and optionally `GEMINI_MODEL`. Use a long random `FLASK_SECRET_KEY`; do not use the development default.
4. Deploy and open `/api/health`. Confirm `ai_configured` is true.
5. Run an end-to-end session: upload a text-based PDF/DOCX, select a domain, generate questions, exercise typing and browser voice controls, submit, and print/save the report.

Vercel Python functions are serverless and have plan-specific execution limits. Resume analysis, generation, and evaluation each call Gemini and may take several seconds; configure a suitable function duration in Vercel project settings within the plan limit if needed. Python runtime support and limits can change; check Vercel's current documentation before deployment. Use the Vercel deployment/runtime logs for platform errors. Application errors are returned as structured messages without stack traces.

## Security, privacy, and limitations

- Original resume bytes and extracted text are processed per request and are not written to disk or logs. Resume text is sent to the configured Google Gemini service for analysis.
- Interview state is encrypted and authenticated with Fernet; the token is a bearer credential and expires after eight hours. Do not share it. Correct answers and rubrics are absent from public question data.
- Stateless serverless deployment avoids Python global state and local persistence. This means there is no permanent history, account system, or server-side one-time submission ledger. A copied token can be replayed until expiry. Add a persistent database and user/session authentication before offering durable or abuse-resistant history.
- Rate limiting across serverless invocations requires an external store and is not included. Configure provider quotas and platform protections for public deployments.
- Gemini output can be wrong or unavailable. Automated scoring validates schema and bounds, but AI feedback is for practice, not hiring advice.
- Browser voice support depends on browser, operating system, and microphone permissions. Text input remains available. The app does not infer speaking quality from typed answers.
- Scanned PDF OCR, persistent history, user accounts, and permanent report storage are not implemented.

## Troubleshooting

- `Gemini is not configured`: add `GEMINI_API_KEY` locally or in Vercel and redeploy after changing production variables.
- Model/access or quota errors: verify the configured model name and key access in Google AI Studio, and check provider quota and Vercel function logs.
- Resume rejected: use a valid PDF with selectable text or a DOCX file under 4 MB. Password-protected files and scanned image-only PDFs are unsupported.
- Session expired: start a new session; encrypted session tokens expire after eight hours and browser sessionStorage can be cleared by browser settings.
- Microphone button unavailable: allow microphone permission and use a browser with Web Speech recognition support, or type the response.
