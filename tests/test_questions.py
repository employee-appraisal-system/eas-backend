from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)


def test_add_descriptive_question():
    payload = {
        "question_type": "Descriptive",
        "question_text": "Do you live movies?",
        "options": None,
    }
    response = client.post("/question", json=payload)
    assert response.status_code == 201
    assert response.json() == {"message": "Question added successfully"}


def test_add_mcq_question():
    payload = {
        "question_type": "MCQ",
        "question_text": "Which is your favorite team?",
        "options": [
            {"option_text": "MI"},
            {"option_text": "CSK"},
            {"option_text": "KKR"},
        ],
    }
    response = client.post("/question", json=payload)
    assert response.status_code == 201
    assert response.json() == {"message": "Question added successfully"}


def test_yes_no_question():
    payload = {
        "question_type": "Yes/No",
        "question_text": "Do you like testing?",
        "options": [{"option_text": "Yes"}, {"option_text": "No"}],
    }
    response = client.post("/question", json=payload)
    assert response.status_code == 201
    assert response.json() == {"message": "Question added successfully"}


def test_get_all_questions():
    response = client.get("/question")
    assert response.status_code == 200
