import os
import re
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from database import SessionLocal
from crud import get_students, update_student, delete_student
from schemas import StudentCreate

from vector_db import search_students


load_dotenv()


# =========================================================
# STATE
# =========================================================

class ChatState(TypedDict):
    message: str
    response: str


# =========================================================
# CHATBOT NODE
# =========================================================

def chatbot_node(state: ChatState):

    question = state["message"].strip()

    db = SessionLocal()

    try:

        students = get_students(db)

        print(
            f"DEBUG - Students found: {len(students)}"
        )

        for student in students:

            print(
                f"DEBUG - Student: "
                f"{student.name} {student.marks}"
            )


        # =================================================
        # DELETE STUDENT
        # =================================================

        delete_match = re.search(
            r"delete\s+(?:student\s+)?(?:with\s+)?(?:id\s+)?(\d+)$",
            question,
            re.IGNORECASE
        )

        if delete_match:

            student_id = int(
                delete_match.group(1)
            )

            student = next(
                (
                    s for s in students
                    if s.id == student_id
                ),
                None
            )

            if student is None:

                return {
                    "response":
                    f"No student with ID {student_id} was found."
                }

            deleted_name = student.name

            delete_student(
                db,
                student_id
            )

            return {
                "response":
                f"Student deleted successfully.\n\n"
                f"ID: {student_id}\n"
                f"Name: {deleted_name}"
            }


        # =================================================
        # DELETE BY NAME
        # =================================================

        delete_name_match = re.search(
            r"delete\s+(?:student\s+)?(.+)",
            question,
            re.IGNORECASE
        )

        if (
            delete_name_match
            and "id" not in question.lower()
        ):

            student_name = (
                delete_name_match
                .group(1)
                .strip()
            )

            matching_students = [
                s for s in students
                if s.name.lower()
                == student_name.lower()
            ]

            if len(matching_students) == 1:

                student = matching_students[0]

                delete_student(
                    db,
                    student.id
                )

                return {
                    "response":
                    f"Student deleted successfully.\n\n"
                    f"ID: {student.id}\n"
                    f"Name: {student.name}"
                }


        # =================================================
        # UPDATE
        # =================================================

        update_match = re.search(
            r"update\s+(.+?)['’]s\s+"
            r"(marks|email|age|gender|course)\s+to\s+(.+)",
            question,
            re.IGNORECASE
        )

        if update_match:

            student_name = (
                update_match.group(1)
                .strip()
            )

            field = (
                update_match.group(2)
                .lower()
            )

            new_value = (
                update_match.group(3)
                .strip()
            )

            matching_students = [
                s for s in students
                if s.name.lower()
                == student_name.lower()
            ]

            if len(matching_students) == 0:

                return {
                    "response":
                    f"No student named "
                    f"{student_name} was found."
                }

            if len(matching_students) > 1:

                details = "\n".join(
                    f"ID: {s.id}, "
                    f"Email: {s.email}"
                    for s in matching_students
                )

                return {
                    "response":
                    f"There are multiple students "
                    f"named {student_name}.\n\n"
                    f"{details}\n\n"
                    f"Please specify the student ID."
                }

            student = matching_students[0]

            name = student.name
            email = student.email
            age = student.age
            gender = student.gender
            course = student.course
            marks = student.marks


            if field == "marks":

                try:
                    marks = int(new_value)

                except ValueError:

                    return {
                        "response":
                        "Marks must be a number."
                    }


            elif field == "age":

                try:
                    age = int(new_value)

                except ValueError:

                    return {
                        "response":
                        "Age must be a number."
                    }


            elif field == "email":

                email = new_value


            elif field == "gender":

                gender = new_value


            elif field == "course":

                course = new_value


            updated_data = StudentCreate(
                name=name,
                email=email,
                age=age,
                gender=gender,
                course=course,
                marks=marks
            )


            updated_student = update_student(
                db,
                student.id,
                updated_data
            )


            return {
                "response":
                f"Student updated successfully.\n\n"
                f"ID: {updated_student.id}\n"
                f"Name: {updated_student.name}\n"
                f"Email: {updated_student.email}\n"
                f"Age: {updated_student.age}\n"
                f"Gender: {updated_student.gender}\n"
                f"Course: {updated_student.course}\n"
                f"Marks: {updated_student.marks}"
            }


        # =================================================
        # SHOW ALL STUDENTS
        # =================================================

        if re.search(
            r"\b(show|list|display)\b.*\b(all|every)\b.*student",
            question,
            re.IGNORECASE
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
                "response":
                result.strip()
            }


        # =================================================
        # CHROMADB RETRIEVAL
        # =================================================

        try:

            retrieval = search_students(
                question,
                limit=3
            )

            print(
                "DEBUG - ChromaDB Retrieval:",
                retrieval
            )

        except Exception as e:

            print(
                "DEBUG - ChromaDB error:",
                e
            )


        # =================================================
        # FIND STUDENT FROM QUESTION
        # =================================================

        selected_student = None

        for student in students:

            if re.search(
                rf"\b{re.escape(student.name)}\b",
                question,
                re.IGNORECASE
            ):

                selected_student = student
                break


        # =================================================
        # NO STUDENT FOUND
        # =================================================

        if selected_student is None:

            return {
                "response":
                "I could not identify the student. "
                "Please provide the student's name or ID."
            }


        student = selected_student


        # =================================================
        # MARKS
        # =================================================

        if re.search(
            r"\b(marks|mark|score|scores)\b",
            question,
            re.IGNORECASE
        ):

            return {
                "response":
                f"{student.name}'s marks are "
                f"{student.marks}."
            }


        # =================================================
        # EMAIL
        # =================================================

        if re.search(
            r"\b(email|mail)\b",
            question,
            re.IGNORECASE
        ):

            return {
                "response":
                f"{student.name}'s email is "
                f"{student.email}."
            }


        # =================================================
        # COURSE
        # =================================================

        if re.search(
            r"\b(course|studying)\b",
            question,
            re.IGNORECASE
        ):

            return {
                "response":
                f"{student.name} is studying "
                f"{student.course}."
            }


        # =================================================
        # AGE
        # =================================================

        if re.search(
            r"\bage\b",
            question,
            re.IGNORECASE
        ):

            return {
                "response":
                f"{student.name}'s age is "
                f"{student.age}."
            }


        # =================================================
        # GENDER
        # =================================================

        if re.search(
            r"\b(gender|sex)\b",
            question,
            re.IGNORECASE
        ):

            return {
                "response":
                f"{student.name}'s gender is "
                f"{student.gender}."
            }


        # =================================================
        # DETAILS
        # =================================================

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


    finally:

        db.close()


# =========================================================
# LANGGRAPH
# =========================================================

builder = StateGraph(
    ChatState
)

builder.add_node(
    "chatbot",
    chatbot_node
)

builder.add_edge(
    START,
    "chatbot"
)

builder.add_edge(
    "chatbot",
    END
)

graph = builder.compile()


# =========================================================
# TERMINAL CHATBOT
# =========================================================

print(
    "==================================="
)

print(
    " Student Management AI Chatbot"
)

print(
    " Type 'exit' to stop"
)

print(
    "==================================="
)


while True:

    question = input(
        "\nYou: "
    )

    if question.lower().strip() == "exit":

        print(
            "Goodbye!"
        )

        break


    result = graph.invoke(
        {
            "message": question,
            "response": ""
        }
    )


    print(
        "\nAI:",
        result["response"]
    )