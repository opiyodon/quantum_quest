from database import db
from models import Question

def populate_questions():
    questions = [
        {
            "subject": "Physics",
            "difficulty": "Easy",
            "question_text": "What is the speed of light in vacuum?",
            "correct_answer": "299,792,458 meters per second",
            "explanation": "The speed of light in vacuum, commonly denoted as c, is a fundamental constant in physics."
        },
        {
            "subject": "Astronomy",
            "difficulty": "Medium",
            "question_text": "What is a black hole?",
            "correct_answer": "A region of spacetime where gravity is so strong that nothing can escape from it",
            "explanation": "Black holes are formed when massive stars collapse at the end of their life cycle."
        },
        {
            "subject": "Quantum Mechanics",
            "difficulty": "Hard",
            "question_text": "What is the Heisenberg Uncertainty Principle?",
            "correct_answer": "It is impossible to simultaneously measure both the position and momentum of a particle with absolute precision",
            "explanation": "This principle is fundamental to quantum mechanics and sets limits on the precision of certain pairs of physical properties of a particle."
        }
    ]

    for q in questions:
        Question.create(**q)

    print("Database populated with sample questions.")

if __name__ == "__main__":
    populate_questions()
