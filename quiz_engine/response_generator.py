import spacy

nlp = spacy.load("en_core_web_sm")

def generate_response(user_input):
    doc = nlp(user_input.lower())
    
    if any(token.text in ["start", "begin", "quiz"] for token in doc):
        return "start_quiz"
    elif any(token.text in ["progress", "score", "performance"] for token in doc):
        return "show_progress"
    elif any(token.text in ["hint", "help"] for token in doc):
        return "provide_hint"
    else:
        return "answer_question"
