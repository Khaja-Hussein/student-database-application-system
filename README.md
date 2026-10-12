# 🎓 Student Database Application System – Backend

A backend application that manages student records and provides an AI-powered chatbot to answer questions about student information. Built using FastAPI, SQLAlchemy, ChromaDB, LangGraph, and Gemini API integration.

## 🚀 Features

- Create, read, update, and delete student records.
- Manage student information using a SQLite database.
- Provide REST APIs using FastAPI.
- Interactive API documentation using Swagger UI.
- Search student information using ChromaDB vector database.
- AI chatbot for answering questions about student records.
- LangGraph-based chatbot workflow.
- Gemini API integration for AI-generated responses.
- Web-based frontend for interacting with the application.
- Docker support for containerization and deployment.

## 🛠️ Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ChromaDB
- LangGraph
- Google Gemini API
- HTML
- CSS
- JavaScript
- Docker
- Git and GitHub

## 🤖 AI Chatbot

The chatbot allows users to ask questions about student records using natural language.

Example questions:

- What are Khaja's marks?
- What is Khaja's email?
- What is Khaja's course?
- Show me Khaja's details.
- Show all students.

Example response:

**User:** What are Khaja's marks?

**AI:** Khaja's marks are 98.

**User:** What is Khaja's course?

**AI:** Khaja is studying Artificial Intelligence.

**Note:** The chatbot's student-question functionality has been tested. Live Gemini API access was restricted during development, so successful live Gemini generation has not been confirmed.

## 📂 Project Structure

```text
student_management_project/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── chatbot.py
├── crud.py
├── database.py
├── main.py
├── models.py
├── schemas.py
├── vector_db.py
├── test_gemini.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/students/` | Create a student |
| GET | `/students/` | Retrieve all students |
| GET | `/students/{student_id}` | Retrieve a student by ID |
| PUT | `/students/{student_id}` | Update student information |
| DELETE | `/students/{student_id}` | Delete a student |
| POST | `/chat` | Ask the AI chatbot a question |

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Khaja-Hussein/student-database-application-system.git
```

### 2. Open the Project Directory

```bash
cd student-database-application-system
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Replace `your_gemini_api_key` with a valid API key. Never commit `.env` or expose your API key publicly.

### 5. Run the Application

```bash
python -m uvicorn main:app --reload
```

Open the application in your browser:

http://127.0.0.1:8000/

## 📖 Swagger API Documentation

FastAPI automatically generates interactive API documentation.

Open:

http://127.0.0.1:8000/docs

Use Swagger UI to test the student CRUD endpoints and chatbot API.

## 🗄️ Vector Database

ChromaDB is used to store and retrieve student information through vector-based search.

This helps retrieve relevant student records when users ask questions through the chatbot.

## 🐳 Docker

### Build the Docker Image

```bash
docker build -t student-management .
```

### Run the Container

```bash
docker run -p 8000:8000 student-management
```

Open the application:

http://127.0.0.1:8000/

## 🎯 Project Objective

The objective of this project is to develop a modular student database backend that combines REST APIs, database management, vector search, and a chatbot workflow to make student information easier to manage and retrieve.

## ⚠️ Limitations

- AI-generated responses depend on Gemini API availability and valid project access.
- The application requires appropriate environment configuration for Gemini integration.
- Student information returned by the chatbot depends on the records available in the database.

## 👨‍💻 Author

**Khaja Hussein**

B.Tech – Artificial Intelligence