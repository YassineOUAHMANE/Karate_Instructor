const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");
const navbar = document.getElementById("navbar");

sign_up_btn.addEventListener("click", () => {
    container.classList.add("sign-up-mode");
    navbar.classList.add("hidden"); // Hide the navbar during the movement
    setTimeout(() => {
        navbar.classList.remove("move-left"); // Reset position
        navbar.classList.add("move-right"); // Move navbar to the right
        navbar.classList.remove("hidden"); // Show the navbar after the movement
    }, 1000);
});

sign_in_btn.addEventListener("click", () => {
    container.classList.remove("sign-up-mode");
    navbar.classList.add("hidden");
    setTimeout(() => {
        navbar.classList.remove("move-right"); // Reset position
        navbar.classList.add("move-left"); // Move navbar back to the left
        navbar.classList.remove("hidden"); // Show the navbar after the movement
    }, 1000);
});
