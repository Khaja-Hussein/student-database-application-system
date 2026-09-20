from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
import schemas
import crud

from database import engine, SessionLocal

# ChromaDB
from vector_db import (
    add_student_to_vector_db,
    delete_student_from_vector_db
)

# AI Chatbot
from chatbot import ask_ai


# =========================================================
# DATABASE
# =========================================================

models.Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Student Database Application System",
    description="Student Database Backend with FastAPI, ChromaDB, LangGraph and Gemini",
    version="1.0.0"
)


# =========================================================
# DATABASE SESSION
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# CREATE STUDENT
# =========================================================

@app.post(
    "/students/",
    response_model=schemas.StudentResponse
)
def create_student(
    student: schemas.StudentCreate,
    db: Session = Depends(get_db)
):

    new_student = crud.create_student(
        db,
        student
    )

    # Add student to ChromaDB
    add_student_to_vector_db(new_student)

    return new_student


# =========================================================
# GET ALL STUDENTS
# =========================================================

@app.get(
    "/students/",
    response_model=list[schemas.StudentResponse]
)
def read_students(
    db: Session = Depends(get_db)
):

    return crud.get_students(db)


# =========================================================
# GET ONE STUDENT
# =========================================================

@app.get(
    "/students/{student_id}",
    response_model=schemas.StudentResponse
)
def read_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = crud.get_student(
        db,
        student_id
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


# =========================================================
# UPDATE STUDENT
# =========================================================

@app.put(
    "/students/{student_id}",
    response_model=schemas.StudentResponse
)
def update_student(
    student_id: int,
    student: schemas.StudentCreate,
    db: Session = Depends(get_db)
):

    updated_student = crud.update_student(
        db,
        student_id,
        student
    )

    if updated_student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Update ChromaDB
    add_student_to_vector_db(updated_student)

    return updated_student


# =========================================================
# DELETE STUDENT
# =========================================================

@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = crud.get_student(
        db,
        student_id
    )

    if student is None:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    crud.delete_student(
        db,
        student_id
    )

    # Remove from ChromaDB
    delete_student_from_vector_db(
        student_id
    )

    return {
        "message": "Student deleted successfully",
        "id": student_id,
        "name": student.name
    }


# =========================================================
# AI CHAT
# =========================================================

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):

    question = request.message.strip()

    if not question:

        return {
            "response": "Please enter a question."
        }

    try:

        answer = ask_ai(question)

        return {
            "response": answer
        }

    except Exception as e:

        print("Chat error:", e)

        return {
            "response": "Sorry, I could not process your question."
        }


# =========================================================
# FRONTEND
# =========================================================

app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)