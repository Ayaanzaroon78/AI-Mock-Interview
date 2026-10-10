import pytest
from backend.question_service import DOMAINS, fallback, validate_questions


def valid():
    return {"mcqs": [{"question":"Q", "options":{"A":"a","B":"b","C":"c","D":"d"},"answer":"A","explanation":"why","difficulty":"easy","topic":"t","reference":"Python"} for _ in range(5)],
            "theory": [{"question":"Q", "topic":"t", "difficulty":"easy", "rubric":"r", "model_answer":"m"} for _ in range(5)]}


def test_exactly_five_and_five():
    assert len(validate_questions(valid())["mcqs"]) == 5
    assert len(validate_questions(valid())["theory"]) == 5


def test_rejects_wrong_count_options_and_answer():
    data=valid();data["mcqs"].pop()
    with pytest.raises(ValueError):validate_questions(data)
    data=valid();data["mcqs"][0]["options"].pop("D")
    with pytest.raises(ValueError):validate_questions(data)
    data=valid();data["mcqs"][0]["answer"]="E"
    with pytest.raises(ValueError):validate_questions(data)


def test_fallback_is_domain_relevant_and_personalized():
    data=fallback({"skills":["Flask"]},"Python Full Stack Development")
    assert len(data["mcqs"]) == len(data["theory"]) == 5
    assert all(q["reference"] == "Flask" for q in data["mcqs"])
    assert len(DOMAINS) == 6
