from backend.evaluation_service import score_report
from backend.question_service import fallback


def config(): return {"GEMINI_API_KEY":"configured", "GEMINI_MODEL":"mock"}
def state():
    p={"skills":["Python"],"experience_level":"Unknown"}
    return {"domain":"Python Full Stack Development","profile":p,"questions":fallback(p,"Python Full Stack Development")}
def answers(keys=None):
    keys=keys or ["A"]*10
    return [{"index":i,"answer":keys[i]} for i in range(10)]


def test_correct_and_incorrect_mcq_scoring_and_formula(monkeypatch):
    def mock_ai(*args, **kwargs):
        return {"summary":"A useful practice session.","strengths":["Reasoning"],"practice_next":["Practice tests"]} if "overall technical" in args[1] else {"evaluations":[{"score":3,"summary":"Good","strengths":["Reasoning"],"missing":["Tests"],"improvement":"Add tests"} for _ in range(5)]}
    monkeypatch.setattr("backend.evaluation_service.generate_json",mock_ai)
    report=score_report(config(),state(),answers(["A","B","A","B","A","Response","Response","Response","Response","Response"]))
    assert report["mcq_score"] == 3
    assert report["theory_score"] == 15
    assert report["raw_score"] == 18
    assert report["percentage"] == 60
    assert report["final_score"] == 6


def test_missing_malformed_and_oversized_answers():
    import pytest
    with pytest.raises(ValueError):score_report(config(),state(),answers()[:9])
    with pytest.raises(ValueError):score_report(config(),state(),[{"index":i,"answer":""} for i in range(10)])
    too_long=answers();too_long[6]["answer"]="x"*5001
    with pytest.raises(ValueError):score_report(config(),state(),too_long)


def test_rejects_invalid_theory_score(monkeypatch):
    import pytest
    monkeypatch.setattr("backend.evaluation_service.generate_json",lambda *a,**k:{"evaluations":[{"score":8} for _ in range(5)]})
    with pytest.raises(ValueError):score_report(config(),state(),answers())
