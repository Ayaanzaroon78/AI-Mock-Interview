import json
from backend.gemini_service import generate_json

DOMAINS = {
    "Cybersecurity": "network security, authentication, authorization, OWASP, encryption, secure coding, vulnerabilities and incident response",
    "Python Full Stack Development": "Python, Flask, Django, REST APIs, SQL, databases, HTML, CSS, JavaScript, testing and deployment",
    "Java Full Stack Development": "Java, OOP, collections, Spring Boot, REST APIs, SQL, web frontend and deployment",
    "Data Analysis": "SQL, Python, Pandas, data cleaning, EDA, statistics, visualization and business insights",
    "Data Science": "probability, statistics, feature engineering, evaluation, regression, classification and experimentation",
    "AI/ML Engineer": "supervised and unsupervised learning, evaluation, overfitting, neural networks, embeddings, deployment and MLOps",
}


def validate_questions(data):
    if not isinstance(data, dict) or not isinstance(data.get("mcqs"), list) or not isinstance(data.get("theory"), list):
        raise ValueError("Question response has an invalid structure.")
    if len(data["mcqs"]) != 5 or len(data["theory"]) != 5:
        raise ValueError("Question set must contain exactly five MCQs and five theory questions.")
    for q in data["mcqs"]:
        if not all(isinstance(q.get(k), str) and q[k].strip() for k in ("question", "topic", "difficulty", "explanation", "reference")):
            raise ValueError("An MCQ is missing required text fields.")
        if not isinstance(q.get("options"), dict) or set(q["options"]) != {"A", "B", "C", "D"} or not all(isinstance(v, str) and v for v in q["options"].values()):
            raise ValueError("Each MCQ must have four labeled options.")
        if q.get("answer") not in {"A", "B", "C", "D"}:
            raise ValueError("An MCQ answer key is invalid.")
    for q in data["theory"]:
        if not all(isinstance(q.get(k), str) and q[k].strip() for k in ("question", "topic", "difficulty", "rubric", "model_answer")):
            raise ValueError("A theoretical question is missing required fields.")
    return data


def fallback(profile, domain):
    skills = profile.get("skills", []) or profile.get("programming_languages", []) or ["core technical concepts"]
    skill = skills[0]
    topics = DOMAINS[domain].split(", ")
    mcqs = []
    for i in range(5):
        topic = topics[i % len(topics)]
        mcqs.append({"question": f"Which approach best demonstrates sound practice for {topic} in a {skill}-related context?", "options": {"A": "Validate inputs and handle expected failures", "B": "Trust all external data", "C": "Skip testing and monitoring", "D": "Store secrets in source code"}, "answer": "A", "explanation": "Validation and explicit failure handling improve reliability and security.", "difficulty": "Foundational", "topic": topic, "reference": skill})
    theory = [{"question": f"Describe how you would apply {topic} to solve a practical problem, including trade-offs and validation.", "topic": topic, "difficulty": "Intermediate", "rubric": f"Correct concepts, practical steps, trade-offs, validation and relevance to {topic}.", "model_answer": f"A strong answer defines the goal, outlines an implementation using {topic}, considers constraints and trade-offs, and validates the result with tests or measurable evidence."} for topic in topics[:5]]
    return {"mcqs": mcqs, "theory": theory}


def make_questions(config, profile, domain):
    instruction = "Create exactly five personalized technical MCQs and five open-ended theory interview questions. MCQs must have exactly four options A-D and one correct answer key. Personalize first five with actual resume skills/projects only. Theory needs rubric and model_answer. Return JSON object with mcqs and theory arrays."
    for _ in range(2):
        try:
            data = validate_questions(generate_json(config, instruction, {"profile": profile, "domain": domain, "topics": DOMAINS[domain]}))
            return data, "resume-personalized"
        except Exception:
            continue
    return validate_questions(fallback(profile, domain)), "domain fallback; personalization limited"
