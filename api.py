import os
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

from database import (
    CategoryInUseError,
    CategoryNameAlreadyExistsError,
    CategoryNotFoundError,
    QuestionAlreadyAnsweredError,
    create_category_in_db,
    create_question_in_db,
    create_quiz_session,
    create_tables,
    delete_category_from_db,
    delete_question_from_db,
    get_admin_categories_from_db,
    get_categories_from_db,
    get_question_from_db,
    get_questions_from_db,
    get_quiz_score,
    is_postgres,
    save_quiz_answer,
    seed_questions,
    update_category_in_db,
    update_question_in_db,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not is_postgres():
        create_tables()
        seed_questions()
    yield


app = FastAPI(title="Prepositions Quiz API", lifespan=lifespan)
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://my-quiz-blond.vercel.app",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        raise HTTPException(
            status_code=503, detail="Admin authentication is not configured"
        )
    username_is_correct = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        admin_username.encode("utf-8"),
    )

    password_is_correct = secrets.compare_digest(
        credentials.password.encode("utf-8"), admin_password.encode("utf-8")
    )

    if not (username_is_correct and password_is_correct):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class AnswerRequest(BaseModel):
    session_id: int = Field(gt=0)
    question_id: int = Field(ge=0)
    answer: int = Field(ge=1, le=3)


class SessionRequest(BaseModel):
    category: str | None = None


class AdminQuestionRequest(BaseModel):
    category: str = Field(min_length=1)
    question: str = Field(min_length=1)
    full_answer: str = Field(min_length=1)
    correct_answer: int = Field(ge=1, le=3)
    answers: list[str] = Field(min_length=3, max_length=3)


class AdminCategoryRequest(BaseModel):
    name: str = Field(min_length=1)


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


@app.get("/admin/questions")
def admin_read_questions(
    admin: str = Depends(verify_admin),
):
    return {"questions": get_questions_from_db()}


@app.put("/admin/questions/{question_id}")
def admin_update_question(
    question_id: int,
    request: AdminQuestionRequest,
    admin: str = Depends(verify_admin),
):
    if question_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="Invalid question ID",
        )

    try:
        update_question_in_db(
            question_id=question_id,
            category=request.category,
            question=request.question,
            full_answer=request.full_answer,
            correct_answer=request.correct_answer,
            answers=request.answers,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return {
        "message": "Question updated successfully",
        "question_id": question_id,
    }


@app.delete("/admin/questions/{question_id}")
def admin_delete_question(
    question_id: int,
    admin: str = Depends(verify_admin),
):
    if question_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="Invalid question ID",
        )

    try:
        delete_question_from_db(question_id)
    except ValueError as error:
        message = str(error)

        status_code = 409 if "quiz results" in message else 404

        raise HTTPException(
            status_code=status_code,
            detail=message,
        ) from error

    return {
        "message": "Question deleted successfully",
        "question_id": question_id,
    }


@app.post("/admin/questions", status_code=201)
def admin_create_question(
    request: AdminQuestionRequest,
    admin: str = Depends(verify_admin),
):
    try:
        question_id = create_question_in_db(
            category=request.category,
            question=request.question,
            full_answer=request.full_answer,
            correct_answer=request.correct_answer,
            answers=request.answers,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return {
        "message": "Question created successfully",
        "question_id": question_id,
    }


@app.post("/admin/categories", status_code=201)
def admin_create_category(
    request: AdminCategoryRequest,
    admin: str = Depends(verify_admin),
):
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Category name cannot be empty",
        )

    category = create_category_in_db(name)

    return {
        "message": "Category created successfully",
        "category": category,
    }


@app.get("/admin/categories")
def admin_get_categories(
    admin: str = Depends(verify_admin),
):
    return {
        "categories": get_admin_categories_from_db(),
    }


@app.put("/admin/categories/{category_id}")
def admin_update_category(
    category_id: int,
    request: AdminCategoryRequest,
    admin: str = Depends(verify_admin),
):
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Category name cannot be empty",
        )

    try:
        category = update_category_in_db(category_id, name)
    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except CategoryNameAlreadyExistsError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return {
        "message": "Category updated successfully",
        "category": category,
    }


@app.delete("/admin/categories/{category_id}")
def admin_delete_category(
    category_id: int,
    admin: str = Depends(verify_admin),
):
    try:
        delete_category_from_db(category_id)
    except CategoryNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except CategoryInUseError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    return {
        "message": "Category deleted successfully",
        "category_id": category_id,
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
