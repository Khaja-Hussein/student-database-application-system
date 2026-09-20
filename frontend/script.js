const API = "";


// ===============================
// LOAD STUDENTS
// ===============================

async function loadStudents() {

    try {

        const response = await fetch(`${API}/students/`);

        const students = await response.json();

        const table = document.getElementById("studentTable");

        table.innerHTML = "";

        students.forEach(student => {

            table.innerHTML += `
                <tr>
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.email}</td>
                    <td>${student.age}</td>
                    <td>${student.gender}</td>
                    <td>${student.course}</td>
                    <td>${student.marks}</td>

                    <td>
                        <button
                            class="delete-btn"
                            onclick="deleteStudent(${student.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `;

        });

    } catch (error) {

        console.error(error);

        alert("Could not connect to backend.");

    }
}


// ===============================
// ADD STUDENT
// ===============================

document
    .getElementById("studentForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const student = {

            name: document.getElementById("name").value,

            email: document.getElementById("email").value,

            age: Number(document.getElementById("age").value),

            gender: document.getElementById("gender").value,

            course: document.getElementById("course").value,

            marks: Number(document.getElementById("marks").value)

        };


        try {

            const response = await fetch(`${API}/students/`, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(student)

            });


            if (!response.ok) {

                const error = await response.text();

                alert("Failed to add student:\n" + error);

                return;

            }


            alert("Student added successfully!");

            document.getElementById("studentForm").reset();

            loadStudents();


        } catch (error) {

            console.error(error);

            alert("Backend connection failed.");

        }

    });


// ===============================
// DELETE STUDENT
// ===============================

async function deleteStudent(id) {

    if (!confirm("Delete this student?")) {
        return;
    }


    try {

        const response = await fetch(
            `${API}/students/${id}`,
            {
                method: "DELETE"
            }
        );


        if (!response.ok) {

            alert("Failed to delete student.");

            return;

        }


        alert("Student deleted successfully!");

        loadStudents();


    } catch (error) {

        console.error(error);

        alert("Backend connection failed.");

    }

}


// ===============================
// AI CHATBOT
// ===============================

async function askAI() {

    const input = document.getElementById("question");

    const question = input.value.trim();

    if (!question) {
        return;
    }


    const chatBox = document.getElementById("chatBox");


    chatBox.innerHTML += `
        <div class="message user">
            <b>You:</b> ${question}
        </div>
    `;


    input.value = "";


    try {

        const response = await fetch(`${API}/chat`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: question
            })

        });


        const data = await response.json();


        chatBox.innerHTML += `
            <div class="message ai">
                <b>AI:</b> ${data.response || data.message || JSON.stringify(data)}
            </div>
        `;


        chatBox.scrollTop = chatBox.scrollHeight;


    } catch (error) {

        console.error(error);

        chatBox.innerHTML += `
            <div class="message ai">
                <b>AI:</b> Backend connection failed.
            </div>
        `;

    }

}


// ===============================
// ENTER KEY FOR CHAT
// ===============================

document
    .getElementById("question")
    .addEventListener("keydown", function(event) {

        if (event.key === "Enter") {
            askAI();
        }

    });


// ===============================
// INITIAL LOAD
// ===============================

loadStudents();