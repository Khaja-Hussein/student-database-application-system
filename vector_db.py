import chromadb


# ==========================================
# CHROMA VECTOR DATABASE
# ==========================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)


collection = client.get_or_create_collection(
    name="students"
)


# ==========================================
# ADD STUDENT TO VECTOR DATABASE
# ==========================================

def add_student_to_vector_db(student):

    collection.upsert(
        ids=[str(student.id)],
        documents=[
            f"""
            Student Name: {student.name}
            Email: {student.email}
            Age: {student.age}
            Gender: {student.gender}
            Course: {student.course}
            Marks: {student.marks}
            """
        ],
        metadatas=[
            {
                "student_id": student.id,
                "name": student.name,
                "course": student.course
            }
        ]
    )


# ==========================================
# SEARCH STUDENTS
# ==========================================

def search_students(query, limit=5):

    results = collection.query(
        query_texts=[query],
        n_results=limit
    )

    return results


# ==========================================
# DELETE STUDENT FROM VECTOR DATABASE
# ==========================================

def delete_student_from_vector_db(student_id):

    collection.delete(
        ids=[str(student_id)]
    )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("ChromaDB is working.")

    print(
        "Collection:",
        collection.name
    )