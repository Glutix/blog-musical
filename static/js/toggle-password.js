document.addEventListener("DOMContentLoaded", function () {
    const togglePassword = document.querySelector("#togglePassword");
    const passwordField = document.querySelector("#id_password");

    if (togglePassword && passwordField) {
        togglePassword.addEventListener("click", () => {
            const type = passwordField.type === "password" ? "text" : "password";
            passwordField.type = type;
            togglePassword.innerHTML =
                type === "password"
                    ? '<i class="bi bi-eye"></i>'
                    : '<i class="bi bi-eye-slash"></i>';
        });

        // Opcional: permitir toggle con teclado (Enter o Space)
        togglePassword.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                togglePassword.click();
            }
        });
    }
});
