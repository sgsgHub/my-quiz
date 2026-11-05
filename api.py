from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import (
    QuestionAlreadyAnsweredError,
    create_quiz_session,
    create_tables,
    get_categories_from_db,
    get_question_from_db,
    get_questions_from_db,
    get_quiz_score,
    is_postgres,
    save_quiz_answer,
    seed_questions,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not is_postgres():
        create_tables()
        seed_questions()
    yield


app = FastAPI(title="Prepositions Quiz API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnswerRequest(BaseModel):
    session_id: int = Field(gt=0)
    question_id: int = Field(ge=0)
    answer: int = Field(ge=1, le=3)


class SessionRequest(BaseModel):
    category: str | None = None


@app.post("/quiz/answer")
def submit_answer(request: AnswerRequest):
    question = get_question_from_db(request.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    try:
        result = save_quiz_answer(
            request.session_id,
            request.question_id,
            request.answer,
        )
    except QuestionAlreadyAnsweredError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return {
        "correct": result["correct"],
        "message": "Correct!" if result["correct"] else "Wrong!",
        "full_answer": question["full_answer"] if not result["correct"] else None,
    }


@app.get("/")
def read_root():
    return {"message": "Quiz API is running"}


@app.get("/categories")
def read_categories():
    return {"categories": get_categories_from_db()}


@app.get("/questions")
def read_questions(category: str | None = None):
    if category is not None:
        categories = get_categories_from_db()

        if category not in categories:
            raise HTTPException(status_code=404, detail=f"Unknown category: {category}")

    selected_questions = get_questions_from_db(category)
    return {
        "questions": [
            {
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "answers": item["answers"],
            }
            for item in selected_questions
        ]
    }


@app.post("/quiz/session/")
def start_quiz(request: SessionRequest):
    try:
        session_id = create_quiz_session(request.category)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return {"session_id": session_id}


@app.get("/quiz/session/{session_id}/score")
def read_quiz_score(session_id: int):
    try:
        return get_quiz_score(session_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
