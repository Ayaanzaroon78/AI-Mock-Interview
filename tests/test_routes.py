from backend import create_app
from backend.security import seal


def client():
    app=create_app({"TESTING":True,"SECRET_KEY":"test-secret","GEMINI_API_KEY":"","MAX_UPLOAD_BYTES":4*1024*1024,"MAX_CONTENT_LENGTH":4*1024*1024+128*1024})
    return app.test_client()


def test_health_and_missing_gemini(monkeypatch):
    monkeypatch.setattr("backend.routes.extract_resume",lambda *a,**k:"A readable resume with enough extracted technical experience and details.")
    c=client();r=c.get("/api/health")
    assert r.status_code==200 and r.json["status"]=="ok" and not r.json["ai_configured"]
    r=c.post("/api/resume/analyze",data={"resume":( __import__("io").BytesIO(b"%PDF-"+b"x"*1000),"resume.pdf")},content_type="multipart/form-data")
    assert r.status_code==503


def test_generate_requires_signed_profile_and_valid_domain():
    c=client()
    assert c.post("/api/interview/generate",json={"domain":"bad","profile_token":"bad"}).status_code==400
    token=seal({"skills":["Python"]},"test-secret")
    r=c.post("/api/interview/generate",json={"domain":"Python Full Stack Development","profile_token":token})
    assert r.status_code==200
    assert "answer" not in r.json["interview"]["mcqs"][0]
    assert r.json["interview"]["source"].startswith("domain fallback")


def test_evaluation_rejects_forged_token():
    c=client();r=c.post("/api/interview/evaluate",json={"interview_id":"made-up","interview_token":"fake","answers":[]})
    assert r.status_code==401
