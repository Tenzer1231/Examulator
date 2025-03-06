document.addEventListener("DOMContentLoaded", function () {
    const facultyFilter = document.getElementById("faculty_filter");
    const groupFilter = document.getElementById("group_filter");

    facultyFilter.addEventListener("change", function () {
        const selectedFaculty = this.value;
        Array.from(groupFilter.options).forEach(option => {
            option.style.display = (selectedFaculty === "" || option.dataset.faculty === selectedFaculty) ? "block" : "none";
        });
        groupFilter.value = "";
        filterResults();
    });

    groupFilter.addEventListener("change", filterResults);

    function filterResults() {
        const selectedGroup = groupFilter.value;
        const studentCards = document.querySelectorAll(".student-card");

        studentCards.forEach(card => {
            card.style.display = (selectedGroup === "" || card.dataset.group === selectedGroup) ? "block" : "none";
        });
    }
});

function openModal(resultId) {
    console.log("Вызов openModal, resultId:", resultId); // Логируем вызов
    fetch(`/teacher/get_test_result/${resultId}`)
        .then(response => response.json())
        .then(data => {
            console.log("Ответ API:", data); // Логируем ответ сервера
            document.getElementById("testTitle").innerText = `Результаты теста: ${data.test_title}`;
            let modalBody = document.getElementById("modalBody");
            modalBody.innerHTML = "";

            if (data.answers.length > 0) {
                data.answers.forEach(ans => {
                    modalBody.innerHTML += `<p><strong>Вопрос:</strong> ${ans.question_text}</p>
                                            <p><strong>Ответ:</strong> ${ans.answer_text ? ans.answer_text : "Не указан"}</p>`;
                    if (ans.file_path) {
                        modalBody.innerHTML += `<p><strong>Приложенный файл:</strong></p>
                                                <img src="/static/uploads/${ans.file_path}" width="200px"><br>`;
                    }
                    modalBody.innerHTML += "<hr>";
                });
            } else {
                modalBody.innerHTML = "<p>Нет данных</p>";
            }

            document.getElementById("gradeInput").value = data.grade || "";
            document.getElementById("commentInput").value = data.comments || "";
            document.getElementById("resultId").value = resultId;

            document.getElementById("testModal").style.display = "block";
        })
        .catch(error => console.error("Ошибка запроса:", error));
}


function closeModal() {
    document.getElementById("testModal").style.display = "none";
}

function submitGrade(event) {
    event.preventDefault();

    let resultId = document.getElementById("resultId").value;
    let grade = document.getElementById("gradeInput").value;
    let comment = document.getElementById("commentInput").value;

    fetch("/teacher/update_grade", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            result_id: resultId,
            grade: grade,
            comment: comment
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Ответ сервера при обновлении оценки:", data); // Проверяем ответ

        if (data.error) {
            alert("Ошибка: " + data.error);
        } else {
            alert("Оценка обновлена!");
            closeModal();
            location.reload();
        }
    })
    .catch(error => console.error("Ошибка при обновлении оценки:", error));
}

function filterResults() {
    const selectedGroup = groupFilter.value;
    console.log("Выбранная группа:", selectedGroup);

    studentCards.forEach(card => {
        console.log("Проверяю карточку:", card.dataset.group);
        card.style.display = (selectedGroup === "" || card.dataset.group === selectedGroup) ? "block" : "none";
    });
}
