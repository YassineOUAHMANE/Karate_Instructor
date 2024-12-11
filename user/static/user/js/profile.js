document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.main-nav a');
    const sections = document.querySelectorAll('section');

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const target = button.getAttribute('section');

            sections.forEach(section => {
                if (section.className === target) {
                    section.classList.add('active');
                } else {
                    section.classList.remove('active');
                }
            });
        });
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const martialArtsList = document.getElementById("martialArts");
    const movementsList = document.getElementById("movements");
    const selectedMartialArt = document.getElementById("selectedMartialArt");
    const selectedMovement = document.getElementById("selectedMovement");
    const movementImage = document.getElementById("movementImage");

    martialArtsList.addEventListener("click", (e) => {
        if (e.target.tagName === "LI") {
            const martialArtId = e.target.getAttribute("data-id");

            fetch(`/movements/${martialArtId}/`)
                .then((response) => response.json())
                .then((data) => {
                    selectedMartialArt.textContent = e.target.textContent;

                    movementsList.innerHTML = "";
                    data.movements.forEach((movement) => {
                        const li = document.createElement("li");
                        li.textContent = movement.name;
                        li.setAttribute("data-img", movement.tutorial);
                        movementsList.appendChild(li);
                    });

                    selectedMovement.textContent = "Select a Movement";
                    movementImage.style.display = "none";
                });
        }
    });

    movementsList.addEventListener("click", (e) => {
        if (e.target.tagName === "LI") {
            const imgPath = e.target.getAttribute("data-img");

            selectedMovement.textContent = e.target.textContent;

            movementImage.src = imgPath;
            movementImage.style.display = "block";
        }
    });
});

document.getElementById("logoutButton").addEventListener("click", function (e) {
    e.preventDefault();
    document.getElementById("logoutForm").submit();
});
