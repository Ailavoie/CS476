document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.register-form');
    const modal = document.getElementById('twoFactorModal');
    const codeInput = document.getElementById('codeInput');
    const errorDiv = document.getElementById('errorMessage');
    const verifyBtn = document.getElementById('verifyBtn');
    
    
    // Handle form submission with 2FA
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Run validation
            let email = document.querySelector("#id_username");  
            let password = document.querySelector("#id_password");  
            let formIsValid = true;

            const emailSpan = document.createElement("span");    
            emailSpan.classList.add("error-text"); 
            let emailErrorMessage = email.parentNode;

            if(!validateEmail(email.value)) {  
                email.classList.add("error-box");
                emailSpan.innerHTML = "Invalid email";
                if(emailErrorMessage.lastChild.innerHTML != emailSpan.innerHTML){
                    emailErrorMessage.appendChild(emailSpan);
                }
                formIsValid = false;
            }
            else{
                email.classList.remove("error-box");
                if(emailErrorMessage.lastChild.innerHTML === emailSpan.innerHTML){
                    emailErrorMessage.removeChild(emailErrorMessage.lastChild);
                }        
            }

            const passwordSpan = document.createElement("span");    
            passwordSpan.classList.add("error-text"); 
            let passwordErrorMessage = password.parentNode;

            if(!password.value || password.value.trim() === ""){
                password.classList.add("error-box");
                passwordSpan.innerHTML = "Password is required";
                if(passwordErrorMessage.lastChild.innerHTML != passwordSpan.innerHTML){
                    passwordErrorMessage.appendChild(passwordSpan);
                }
                formIsValid = false;
            }
            else{
                password.classList.remove("error-box");
                if(passwordErrorMessage.lastChild.innerHTML === passwordSpan.innerHTML){
                    passwordErrorMessage.removeChild(passwordErrorMessage.lastChild);
                }
            }

            if (formIsValid === false){
                e.preventDefault();
    }

            // If validation passes, submit via AJAX for 2FA
            if (formIsValid) {
                const formData = new FormData(loginForm);
                
                console.log('Submitting login form via AJAX...');
                
                fetch(loginForm.action || window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => {
                    return response.text();
                })
                .then(text => {
                    
                    // Check if response looks like HTML
                    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
                        //console.error('ERROR: Server returned HTML instead of JSON');
                        return;
                    }
                    
                    try {
                        const data = JSON.parse(text);
                        console.log('Parsed JSON data:', data);
                        
                        if (data.success && data.requires_2fa) {
                            // Show 2FA modal
                            modal.classList.add('active');
                            codeInput.focus();
                        } else if (data.success) {
                            console.log('Direct login success');
                            // Direct login without 2FA
                            window.location.href = '/';
                        } else {
                            console.log('Login failed:', data.error);
                            // Show error
                        }
                    } catch (e) {
                        console.error('Failed to parse JSON:', e);
                    }
                })
                .catch(error => {
                    console.error('Fetch error:', error);
                });
            }
            
            return false;
        }, true);
    }
    
    // Handle 2FA code verification
    function verify2FACode() {
        const code = codeInput.value.trim();
        
        if (code.length !== 6) {
            errorDiv.textContent = 'Please enter a 6-digit code';
            errorDiv.className = 'error-message';
            return;
        }
        
        verifyBtn.disabled = true;
        verifyBtn.textContent = 'Verifying...';
        
        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch('/accounts/verify-2fa/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                errorDiv.textContent = 'Verification successful! Redirecting...';
                errorDiv.className = 'success-message';
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                errorDiv.textContent = data.error || 'Invalid code. Please try again.';
                errorDiv.className = 'error-message';
                codeInput.value = '';
                codeInput.focus();
                verifyBtn.disabled = false;
                verifyBtn.textContent = 'Verify Code';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            errorDiv.textContent = 'An error occurred. Please try again.';
            errorDiv.className = 'error-message';
            verifyBtn.disabled = false;
            verifyBtn.textContent = 'Verify Code';
        });
    }
    
    // Verify on button click
    if (verifyBtn) {
        verifyBtn.addEventListener('click', verify2FACode);
    }
    
    // Verify on Enter key
    if (codeInput) {
        codeInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                verify2FACode();
            }
        });
        
        // Only allow numbers in code input
        codeInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
            if (this.value.length > 6) {
                this.value = this.value.slice(0, 6);
            }
        });
    }
});