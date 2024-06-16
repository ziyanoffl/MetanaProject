from fastapi import FastAPI, Form, Request, Response, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class Question:
    def __init__(self, id: int, text: str, input_type: str = "text", disclaimer: Optional[str] = None, placeholder: Optional[str] = None):
        self.id = id
        self.text = text
        self.input_type = input_type
        self.disclaimer = disclaimer
        self.placeholder = placeholder

class Answer:
    def __init__(self, question_id: int, answer: str):
        self.question_id = question_id
        self.answer = answer

questions = [
    Question(id=1, text="Before we start, what is your Full name?", placeholder="Full Name"),
    Question(id=2, text="What's your email address? This is how we'll contact you.", input_type="email", placeholder="Email Address"),
    Question(id=3, text="Which country are you from? 🏡🏡🏡", placeholder="Country"),
    Question(id=4, text="What is your phone number?", input_type="tel", placeholder="Phone Number"),
    Question(id=5, text="What languages and frameworks are you familiar with? Select all the languages you know.", input_type="text", placeholder="Languages and Frameworks"),
    Question(id=6, text="How would you describe your current level of coding experience?", input_type="text", placeholder="Coding Experience"),
    Question(id=7, text="What is your current annual compensation? (Optional)", disclaimer="The information provided regarding salary will be kept confidential and will not be used as a determining factor for acceptance into the bootcamp. It will be used exclusively for career advancement guidance.", placeholder="Annual Compensation"),
    Question(id=8, text="Certifying Statement: This question is required. * I hereby acknowledge that this application form was completed by me (the individual seeking to enroll in Metana) and I did not receive help from any external sources. The responses submitted are entirely my own and based on my own reasoning. Also, I opt in to receive communication messages from Metana about my application.", input_type="checkbox"),
    Question(id=9, text="LinkedIn URL (optional)", disclaimer="Here's a snippet link to make your life easy - linkedin.com (It'll open in a new tab) 🚀", input_type="url", placeholder="LinkedIn URL"),
]

# In-memory storage for sessions (for demonstration purposes only)
sessions = {}

def get_questionnaire(session_id: Optional[str] = Cookie(None)) -> List[Answer]:
    if session_id and session_id in sessions:
        return sessions[session_id]
    return []

def save_questionnaire(response: Response, session_id: str, questionnaire: List[Answer]):
    sessions[session_id] = questionnaire
    response.set_cookie(key="session_id", value=session_id)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/start", response_class=HTMLResponse)
async def start_questionnaire(request: Request, session_id: Optional[str] = Cookie(None)):
    questionnaire = get_questionnaire(session_id)
    if len(questionnaire) >= len(questions):
        return templates.TemplateResponse("success.html", {"request": request})

    current_question = questions[len(questionnaire)]
    return templates.TemplateResponse("question.html", {"request": request, "question": current_question, "questionnaire": questionnaire})

@app.post("/submit", response_class=HTMLResponse)
async def submit_answer(request: Request, response: Response, question_id: int = Form(...), answer: str = Form(...), session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(len(sessions) + 1)  # Generate a simple session ID

    questionnaire = get_questionnaire(session_id)

    if question_id <= len(questionnaire):
        questionnaire[question_id - 1].answer = answer
    else:
        questionnaire.append(Answer(question_id=question_id, answer=answer))

    save_questionnaire(response, session_id, questionnaire)
    next_question_id = question_id + 1

    if next_question_id > len(questions):
        return templates.TemplateResponse("success.html", {"request": request})

    next_question = questions[next_question_id - 1]
    return templates.TemplateResponse("question.html", {"request": request, "question": next_question, "questionnaire": questionnaire})

@app.post("/back", response_class=HTMLResponse)
async def go_back(request: Request, question_id: int = Form(...), session_id: Optional[str] = Cookie(None)):
    questionnaire = get_questionnaire(session_id)
    previous_question_id = question_id - 1

    if previous_question_id < 1:
        previous_question_id = 1

    previous_question = questions[previous_question_id - 1]
    return templates.TemplateResponse("question.html", {"request": request, "question": previous_question, "questionnaire": questionnaire})
