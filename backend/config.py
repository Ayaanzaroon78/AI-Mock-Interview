import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "development-only-change-me")
    MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", 4 * 1024 * 1024))
    # Leave room for multipart boundaries and headers under Vercel's 4.5 MB body cap.
    MAX_CONTENT_LENGTH = MAX_UPLOAD_BYTES + 128 * 1024
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
    MIN_RESUME_CHARS = 80
    MAX_ANSWER_CHARS = 5000
