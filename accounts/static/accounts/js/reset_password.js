const passwordInput = document.getElementById('id_password');
const checklist = document.querySelector('.password-checklist');
const form = passwordInput?.closest('form');

if (passwordInput && checklist) {
    passwordInput.addEventListener('input', function() {
        validatePassword(this.value, checklist);
    });
}

// Prevent form submission if password is invalid
if (form && passwordInput) {
    form.addEventListener('submit', function(e) {
        const password = passwordInput.value;
        
        // Check all password requirements
        const hasLength = /.{6,}/.test(password);
        const hasNumber = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
        
        if (!hasLength || !hasNumber || !hasSpecial) {
            e.preventDefault();
            
            // Show error message
            const errorSpan = document.createElement("span");
            errorSpan.classList.add("error-text");
            errorSpan.classList.add("password-submit-error");
            errorSpan.innerHTML = "Please meet all password requirements before submitting";
            
            // Remove any existing error
            const existingError = form.querySelector('.password-submit-error');
            if (existingError) {
                existingError.remove();
            }
            
            // Add error below password field
            passwordInput.parentNode.appendChild(errorSpan);
            passwordInput.classList.add("error-box");
            
            return false;
        }
    });
}