"""AI Mock Interview Flask application package."""

from flask import Flask, jsonify, render_template
from backend.config import Config
from backend.routes import api
import os


def create_app(test_config=None):
    if os.environ.get("VERCEL") and os.environ.get("FLASK_SECRET_KEY", "development-only-change-me") == "development-only-change-me":
        raise RuntimeError("Set a unique FLASK_SECRET_KEY in Vercel before deploying.")
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    app.register_blueprint(api, url_prefix="/api")

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.errorhandler(413)
    def too_large(_):
        return jsonify(error="Request is too large. Resume files must be 4 MB or smaller."), 413

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), geolocation=(), microphone=(self)"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        return response

    return app


app = create_app()
