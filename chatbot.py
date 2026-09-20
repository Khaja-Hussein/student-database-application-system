import os
import re
from typing import TypedDict

from dotenv import load_dotenv
from google import genai
from langgraph.graph import StateGraph, START, END

from database import SessionLocal
from crud import get_students, update_student, delete_student
from schemas import StudentCreate
from vector_db import search_students


load_dotenv()


# =========================================================
# GEMINI
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

gemini_client = None

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# STATE
# =========================================================

class ChatState(TypedDict):
    message: str
    context: str
    response: str


# =========================================================
# RETRIEVAL NODE
# =========================================================

def retrieve_node(state: ChatState):

    question = state["message"].strip()

    db = SessionLocal()

    try:
        students = get_students(db)

        # -------------------------------------------------
        # ChromaDB semantic retrieval
        # -------------------------------------------------

        context = ""

        try:
            results = search_students(
                question,
                limit=5
            )

            documents = results.get(
                "documents",
                [[]]
            )[0]

            if documents:
                context = "\n\n".join(documents)

        except Exception as e:
            print("ChromaDB error:", e)

        # -------------------------------------------------
        # If ChromaDB has no result, use database context
        # -------------------------------------------------

        if not context:

            context = "\n\n".join(
                [
                    f"""
ID: {student.id}
Name: {student.name}
Email: {student.email}
Age: {student.age}
Gender: {student.gender}
Course: {student.course}
Marks: {student.marks}
""".strip()
                    for student in students
                ]
            )

        return {
            "context": context
        }

    finally:
        db.close()


# =========================================================
# FALLBACK ANSWER
# =========================================================

def fallback_answer(question):

    db = SessionLocal()

    try:

        students = get_students(db)

        if not students:
            return "There are no students in the database."

        # -------------------------------------------------
        # SHOW ALL
        # -------------------------------------------------

        if re.search(
            r"\b(show|list|display)\b.*\b(all|every)\b.*student",
            question,
            re.IGNORECASE
        ) or question.lower() in [
            "show all students",
            "list all students",
            "display all students"
        ]:

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

            return result.strip()

        # -------------------------------------------------
        # FIND STUDENT
        # -------------------------------------------------

        selected_student = None

        id_match = re.search(
            r"(?:id|student id)\s*(?:is|=)?\s*(\d+)",
            question,
            re.IGNORECASE
        )

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
                return (
                    f"No student with ID "
                    f"{student_id} was found."
                )

        else:

            for student in students:

                if re.search(
                    rf"\b{re.escape(student.name)}\b",
                    question,
                    re.IGNORECASE
                ):
                    selected_student = student
                    break

        if selected_student is None:

            return (
                "I could not identify the student. "
                "Please provide the student's name or ID."
            )

        student = selected_student

        # -------------------------------------------------
        # MARKS
        # -------------------------------------------------

        if re.search(
            r"\b(marks|mark|score|scores)\b",
            question,
            re.IGNORECASE
        ):

            return (
                f"{student.name}'s marks are "
                f"{student.marks}."
            )

        # -------------------------------------------------
        # EMAIL
        # -------------------------------------------------

        if re.search(
            r"\b(email|mail)\b",
            question,
            re.IGNORECASE
        ):

            return (
                f"{student.name}'s email is "
                f"{student.email}."
            )

        # -------------------------------------------------
        # COURSE
        # -------------------------------------------------

        if re.search(
            r"\b(course|studying|study)\b",
            question,
            re.IGNORECASE
        ):

            return (
                f"{student.name} is studying "
                f"{student.course}."
            )

        # -------------------------------------------------
        # AGE
        # -------------------------------------------------

        if re.search(
            r"\bage\b",
            question,
            re.IGNORECASE
        ):

            return (
                f"{student.name}'s age is "
                f"{student.age}."
            )

        # -------------------------------------------------
        # GENDER
        # -------------------------------------------------

        if re.search(
            r"\b(gender|sex)\b",
            question,
            re.IGNORECASE
        ):

            return (
                f"{student.name}'s gender is "
                f"{student.gender}."
            )

        # -------------------------------------------------
        # DETAILS
        # -------------------------------------------------

        if re.search(
            r"\b(details|information|info)\b",
            question,
            re.IGNORECASE
        ):

            return (
                f"ID: {student.id}\n"
                f"Name: {student.name}\n"
                f"Email: {student.email}\n"
                f"Age: {student.age}\n"
                f"Gender: {student.gender}\n"
                f"Course: {student.course}\n"
                f"Marks: {student.marks}"
            )

        return (
            f"Student found:\n\n"
            f"ID: {student.id}\n"
            f"Name: {student.name}\n"
            f"Email: {student.email}\n"
            f"Age: {student.age}\n"
            f"Gender: {student.gender}\n"
            f"Course: {student.course}\n"
            f"Marks: {student.marks}"
        )

    finally:
        db.close()


# =========================================================
# GEMINI NODE
# =========================================================

def generate_node(state: ChatState):

    question = state["message"]
    context = state["context"]

    # -----------------------------------------------------
    # Try Gemini
    # -----------------------------------------------------

    if gemini_client:

        prompt = f"""
You are the AI assistant for a Student Database Application System.

Answer the user's question using ONLY the student information
provided in the context.

Do not invent student information.

Be concise and clear.

Student database context:
{context}

User question:
{question}
"""

        try:

            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            if response.text:
                return {
                    "response": response.text.strip()
                }

        except Exception as e:

            print(
                "Gemini unavailable:",
                e
            )

    # -----------------------------------------------------
    # Safe fallback
    # -----------------------------------------------------

    return {
        "response": fallback_answer(question)
    }


# =========================================================
# LANGGRAPH
# =========================================================

builder = StateGraph(ChatState)

builder.add_node(
    "retrieve",
    retrieve_node
)

builder.add_node(
    "generate",
    generate_node
)

builder.add_edge(
    START,
    "retrieve"
)

builder.add_edge(
    "retrieve",
    "generate"
)

builder.add_edge(
    "generate",
    END
)

graph = builder.compile()


# =========================================================
# PUBLIC FUNCTION
# =========================================================

def ask_ai(question: str):

    result = graph.invoke(
        {
            "message": question,
            "context": "",
            "response": ""
        }
    )

    return result["response"]


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("===================================")
    print(" Student Management AI Chatbot")
    print(" Type 'exit' to stop")
    print("===================================")

    while True:

        question = input("\nYou: ")

        if question.lower().strip() == "exit":
            print("Goodbye!")
            break

        answer = ask_ai(question)

        print("\nAI:", answer)