const facultyFilter = document.getElementById("facultyFilter");
const groupFilter = document.getElementById("groupFilter");
const studentCards = document.querySelectorAll(".student-card");

function filterResults() {
    const selectedFaculty = facultyFilter.value;
    const selectedGroup = groupFilter.value;
    studentCards.forEach(card => {
        const cardFaculty = card.dataset.faculty;
        const cardGroup = card.dataset.group;
        if ((selectedFaculty === "" || cardFaculty === selectedFaculty) &&
            (selectedGroup === "" || cardGroup === selectedGroup)) {
            card.style.display = "block";
        } else {
            card.style.display = "none";
        }
    });
}

facultyFilter.addEventListener("change", filterResults);
groupFilter.addEventListener("change", filterResults);
