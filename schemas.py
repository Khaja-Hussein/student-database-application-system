from pydantic import BaseModel, EmailStr


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    age: int
    gender: str
    course: str
    marks: int


class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    gender: str
    course: str
    marks: int

    class Config:
        from_attributes = True