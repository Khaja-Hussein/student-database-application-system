from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
import re

import models
import schemas
import crud

from database import engine, SessionLocal

# ChromaDB
from vector_db import (
    add_student_to_vector_db,
    delete_student_from_vector_db
)


# =========================================================
# DATABASE
# =========================================================

models.Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="Student Management System"
)


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
# CHAT
# =========================================================

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    question = request.message.strip()

    students = crud.get_students(db)

    if not students:
        return {
            "response": "There are no students in the database."
        }


    # =====================================================
    # SHOW ALL STUDENTS
    # =====================================================

    if (
        re.search(
            r"\b(show|list|display)\b.*\b(all|every)\b.*student",
            question,
            re.IGNORECASE
        )
        or question.lower() in [
            "show all students",
            "list all students",
            "display all students"
        ]
    ):

        result = "All students:\n\n"

        for student in students:

            result += (
                f"ID: {student.id}\n"
                f"Name: {student.name}\n"
                f"Email: {student.email}\n"
                f"Age: {student.age}\n"
                f"Gender: {student.gender}\n"
                f"Course: {student.course}\n"
                f"Marks: {student.marks}\n\n"
            )

        return {
            "response": result.strip()
        }


    # =====================================================
    # FIND STUDENT BY ID
    # =====================================================

    id_match = re.search(
        r"(?:id|student id)\s*(?:is|=)?\s*(\d+)",
        question,
        re.IGNORECASE
    )

    selected_student = None

    if id_match:

        student_id = int(
            id_match.group(1)
        )

        selected_student = next(
            (
                s for s in students
                if s.id == student_id
            ),
            None
        )

        if selected_student is None:
            return {
                "response":
                f"No student with ID {student_id} was found."
            }


    # =====================================================
    # FIND STUDENT BY NAME
    # =====================================================

    if selected_student is None:

        for student in students:

            if re.search(
                rf"\b{re.escape(student.name)}\b",
                question,
                re.IGNORECASE
            ):

                selected_student = student
                break


    # =====================================================
    # STUDENT NOT FOUND
    # =====================================================

    if selected_student is None:

        return {
            "response":
            "I could not identify the student. Please provide the student's name or ID."
        }


    student = selected_student


    # =====================================================
    # MULTIPLE STUDENTS WITH SAME NAME
    # =====================================================

    same_name = [
        s for s in students
        if s.name.lower() == student.name.lower()
    ]

    if len(same_name) > 1 and not id_match:

        details = "\n".join(
            f"ID: {s.id}, Email: {s.email}"
            for s in same_name
        )

        return {
            "response":
            f"There are multiple students named {student.name}.\n\n"
            f"{details}\n\n"
            f"Please specify the student ID."
        }


    # =====================================================
    # MARKS
    # =====================================================

    if re.search(
        r"\b(marks|mark|score|scores)\b",
        question,
        re.IGNORECASE
    ):

        return {
            "response":
            f"{student.name}'s marks are {student.marks}."
        }


    # =====================================================
    # EMAIL
    # =====================================================

    if re.search(
        r"\b(email|mail)\b",
        question,
        re.IGNORECASE
    ):

        return {
            "response":
            f"{student.name}'s email is {student.email}."
        }


    # =====================================================
    # COURSE
    # =====================================================

    if re.search(
        r"\b(course|studying)\b",
        question,
        re.IGNORECASE
    ):

        return {
            "response":
            f"{student.name} is studying {student.course}."
        }


    # =====================================================
    # AGE
    # =====================================================

    if re.search(
        r"\bage\b",
        question,
        re.IGNORECASE
    ):

        return {
            "response":
            f"{student.name}'s age is {student.age}."
        }


    # =====================================================
    # GENDER
    # =====================================================

    if re.search(
        r"\b(gender|sex)\b",
        question,
        re.IGNORECASE
    ):

        return {
            "response":
            f"{student.name}'s gender is {student.gender}."
        }


    # =====================================================
    # DETAILS
    # =====================================================

    if re.search(
        r"\b(details|information|info)\b",
        question,
        re.IGNORECASE
    ):

        return {
            "response":
            f"ID: {student.id}\n"
            f"Name: {student.name}\n"
            f"Email: {student.email}\n"
            f"Age: {student.age}\n"
            f"Gender: {student.gender}\n"
            f"Course: {student.course}\n"
            f"Marks: {student.marks}"
        }


    # =====================================================
    # DEFAULT
    # =====================================================

    return {
        "response":
        f"Student found:\n\n"
        f"ID: {student.id}\n"
        f"Name: {student.name}\n"
        f"Email: {student.email}\n"
        f"Age: {student.age}\n"
        f"Gender: {student.gender}\n"
        f"Course: {student.course}\n"
        f"Marks: {student.marks}"
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