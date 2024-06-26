# Quantum Quest: The Interstellar Learning Companion

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Problem Statement](#problem-statement)
4. [How It Works](#how-it-works)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Dataset](#dataset)
8. [Hosting](#hosting)
9. [Contributing](#contributing)
10. [License](#license)

## Introduction

Quantum Quest is an AI-powered educational chatbot designed to make learning science engaging, interactive, and accessible. It covers various scientific disciplines, offering questions that span from basic concepts to cutting-edge theories in physics, astronomy, and space exploration.

## Features

- Interactive quiz-style conversations
- Real-time chat interface
- Natural language processing for understanding user intents
- Adaptive difficulty based on user performance
- Progress tracking across different subjects
- Instant feedback and explanations for answers
- Hint system for challenging questions

## Problem Statement

Quantum Quest addresses several challenges in science education:

1. **Accessibility**: Provides a 24/7 available learning platform, allowing students to learn at their own pace.
2. **Engagement**: Uses an interactive chatbot interface to increase student motivation and retention.
3. **Personalized Learning**: Adapts to individual knowledge levels by offering questions of varying difficulty.
4. **Immediate Feedback**: Offers instant feedback on answers, including explanations, to enhance understanding.
5. **Broad Subject Coverage**: Covers various scientific topics, encouraging exploration of different areas of science.
6. **Self-Assessment**: Enables students to gauge their understanding through quizzes and progress tracking.
7. **Supplementary Learning**: Acts as a companion to traditional learning methods, reinforcing concepts.
8. **STEM Education Support**: Encourages interest in science, technology, engineering, and mathematics.

## How It Works

1. **User Interface**: A web-based chat interface where users interact with the Quantum Quest bot.
2. **Natural Language Processing**: Uses spaCy to analyze user input and determine intent (e.g., start quiz, answer question, request hint).
3. **Quiz Engine**: Selects appropriate questions based on subject and difficulty, checks answers, and manages user progress.
4. **Database**: MongoDB stores questions, user progress, and other relevant data.
5. **Real-time Communication**: Flask-SocketIO enables real-time interaction between the frontend and backend.

Flow:
1. User sends a message through the chat interface.
2. The message is sent to the backend via WebSocket.
3. NLP determines the user's intent.
4. The backend performs the appropriate action based on the intent.
5. The response is sent back to the frontend and displayed in the chat.

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/quantum-quest.git
cd quantum-quest
```

2. Create a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```

3. Install required packages:
```
pip install -r requirements.txt
```

4. Install spaCy English model:
```
python -m spacy download en_core_web_sm
```

5. Set up MongoDB:
- Install MongoDB locally or sign up for a free MongoDB Atlas account.
- Update the `MONGODB_URI` in the `.env` file with your connection string.

6. Populate the database with sample questions:
python populate_db.py

## Usage

1. Start the Flask application:
python app.py

2. Open a web browser and navigate to `http://localhost:5000`.

3. Start interacting with Quantum Quest by typing messages in the chat interface.

## Dataset

The initial dataset of questions is created manually and stored in the `populate_db.py` file. This script populates the MongoDB database with a set of sample questions covering various scientific topics.

To expand the dataset:
1. Add new questions to the `questions` list in `populate_db.py`.
2. Run the script to add the new questions to the database.

For a production environment, consider:
- Partnering with educational institutions or science experts to create a more comprehensive question bank.
- Implementing a content management system for easy addition and modification of questions.
- Integrating with external APIs or databases to dynamically fetch current scientific information and create questions.

## Hosting

To host Quantum Quest, you can use PythonAnywhere, a platform that offers free Python hosting:

1. Sign up for a free account at www.pythonanywhere.com

2. Set up your web app:
- Go to the "Web" tab and create a new web app.
- Choose "Flask" as your web framework.
- Select Python 3.8 as your Python version.

3. Set up your virtual environment:
mkvirtualenv --python=/usr/bin/python3.8 myenv
pip install -r requirements.txt

4. Upload your project files to PythonAnywhere.

5. Modify the WSGI configuration file:
- Navigate to the WSGI configuration file in the Web tab.
- Update it to point to your `app.py` file.

6. Set up environment variables:
- In the "Web" tab, find the "Environment variables" section.
- Add your MongoDB connection string and other necessary variables.

7. Database hosting:
- Sign up for a free MongoDB Atlas account.
- Create a new cluster and obtain the connection string.
- Update your environment variables with the new connection string.
- Whitelist PythonAnywhere's IP addresses in your MongoDB Atlas settings.

8. Install the spaCy English model:
python -m spacy download en_core_web_sm

9. Reload your web app on PythonAnywhere.

Your Quantum Quest app should now be live and accessible via the URL provided by PythonAnywhere.

## Contributing

Contributions to Quantum Quest are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.