from sqlalchemy.orm import Session
from models import Student
from schemas import StudentCreate


def create_student(db: Session, student: StudentCreate):
    new_student = Student(
        name=student.name,
        email=student.email,
        age=student.age,
        gender=student.gender,
        course=student.course,
        marks=student.marks
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


def get_students(db: Session):
    return db.query(Student).all()


def get_student(db: Session, student_id: int):
    return db.query(Student).filter(Student.id == student_id).first()


def update_student(db: Session, student_id: int, student: StudentCreate):
    existing_student = get_student(db, student_id)

    if existing_student is None:
        return None

    existing_student.name = student.name
    existing_student.email = student.email
    existing_student.age = student.age
    existing_student.gender = student.gender
    existing_student.course = student.course
    existing_student.marks = student.marks

    db.commit()
    db.refresh(existing_student)

    return existing_student


def delete_student(db: Session, student_id: int):
    existing_student = get_student(db, student_id)

    if existing_student is None:
        return None

    db.delete(existing_student)
    db.commit()

    return existing_student