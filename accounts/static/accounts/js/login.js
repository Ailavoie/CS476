document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('button[type="submit"]');
    form.addEventListener("click", validateLogin);
});