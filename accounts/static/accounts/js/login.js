document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.register-form');

    if (!loginForm) {
        console.log("login.js: No login/register form on this page. Script stopped.");
        return;
    }
    const modal = document.getElementById('twoFactorModal');
    const codeInput = document.getElementById('codeInput');
    const errorDiv = document.getElementById('errorMessage');
    const verifyBtn = document.getElementById('verifyBtn');
    
    // Forgot password elements
    const forgotPasswordBtn = document.getElementById('forgotPasswordBtn');
    const forgotPasswordModal = document.getElementById('forgotPasswordModal');
    const resetEmailInput = document.getElementById('resetEmailInput');
    const sendResetBtn = document.getElementById('sendResetBtn');
    const cancelResetBtn = document.getElementById('cancelResetBtn');
    const forgotPasswordError = document.getElementById('forgotPasswordError');
    
    console.log('Login page loaded');
    console.log('Form found:', loginForm);
    console.log('Modal found:', modal);
    
    // Handle form submission with 2FA
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            console.log('Form submit event triggered');
            e.preventDefault(); // Prevent default form submission
            e.stopPropagation();
            
            // Run validation
            let email = document.querySelector("#id_username");  
            let password = document.querySelector("#id_password");  
            let formIsValid = true;

            //const emailSpan = document.createElement("span");    
            //emailSpan.classList.add("error-text"); 
            //let emailErrorMessage = email.parentNode;

            //if(!validateEmail(email.value)) {  
            //    email.classList.add("error-box");
            //    emailSpan.innerHTML = "Invalid email";
            //    if(emailErrorMessage.lastChild.innerHTML != emailSpan.innerHTML){
            //        emailErrorMessage.appendChild(emailSpan);
            //    }
            //    formIsValid = false;
            //}
            //else{
            //    email.classList.remove("error-box");
            //    if(emailErrorMessage.lastChild.innerHTML === emailSpan.innerHTML){
            //        emailErrorMessage.removeChild(emailErrorMessage.lastChild);
            //    }        
            //}

            const passwordSpan = document.createElement("span");    
            passwordSpan.classList.add("error-text"); 
            let passwordErrorMessage = password.parentNode;
            console.log(password.value);
            if((!password.value || password.value.trim() === "")){
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
                    console.log('Response status:', response.status);
                    console.log('Response headers:', response.headers.get('content-type'));
                    return response.text();
                })
                .then(text => {
                    console.log('Response text (first 500 chars):', text.substring(0, 500));
                    console.log('Response length:', text.length);
                    
                    // Check if response looks like HTML
                    if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
                        console.error('ERROR: Server returned HTML instead of JSON');
                        console.log('This means the Django view is rendering a template instead of returning JsonResponse');
                        console.log('Check your Django server console for errors');
                        
                        // Show error to user
                        const loginErrorSpan = document.createElement("span");
                        loginErrorSpan.classList.add("error-text");
                        loginErrorSpan.innerHTML = "Server error occurred. Please try again.";
                        const formErrorContainer = loginForm.querySelector('.form-group') || loginForm;
                        if (!formErrorContainer.querySelector('.server-error')) {
                            loginErrorSpan.classList.add('server-error');
                            formErrorContainer.appendChild(loginErrorSpan);
                        }
                        return;
                    }
                    
                    try {
                        const data = JSON.parse(text);
                        console.log('Parsed JSON data:', data);
                        
                        if (data.success && data.requires_2fa) {
                            console.log('Showing 2FA modal...');
                            // Show 2FA modal
                            modal.classList.add('active');
                            codeInput.focus();
                        } else if (data.success) {
                            console.log('Direct login success');
                            // Direct login without 2FA
                            window.location.href = '/';
                        } else {
                            console.log('Login failed:', data.error);
                            // Show error below the form
                            const loginErrorSpan = document.createElement("span");
                            loginErrorSpan.classList.add("error-text");
                            loginErrorSpan.innerHTML = data.error || 'Invalid email or password';
                            
                            // Remove any existing server error messages
                            const existingErrors = loginForm.querySelectorAll('.server-error');
                            existingErrors.forEach(err => err.remove());
                            
                            // Add error after password field
                            loginErrorSpan.classList.add('server-error');
                            passwordErrorMessage.appendChild(loginErrorSpan);
                            
                            // Add error styling to both fields
                            email.classList.add("error-box");
                            password.classList.add("error-box");
                        }
                    } catch (e) {
                        console.error('Failed to parse JSON:', e);
                        console.log('Raw response:', text);
                        
                        // Show error to user
                        const loginErrorSpan = document.createElement("span");
                        loginErrorSpan.classList.add("error-text");
                        loginErrorSpan.classList.add('server-error');
                        loginErrorSpan.innerHTML = "Unexpected server response. Please try again.";
                        
                        const existingErrors = loginForm.querySelectorAll('.server-error');
                        existingErrors.forEach(err => err.remove());
                        
                        passwordErrorMessage.appendChild(loginErrorSpan);
                    }
                })
                .catch(error => {
                    console.error('Fetch error:', error);
                    
                    // Show error to user
                    const loginErrorSpan = document.createElement("span");
                    loginErrorSpan.classList.add("error-text");
                    loginErrorSpan.classList.add('server-error');
                    loginErrorSpan.innerHTML = "Network error. Please check your connection and try again.";
                    
                    const existingErrors = loginForm.querySelectorAll('.server-error');
                    existingErrors.forEach(err => err.remove());
                    
                    const passwordErrorMessage = password.parentNode;
                    passwordErrorMessage.appendChild(loginErrorSpan);
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
    
    // Forgot Password functionality
    if (forgotPasswordBtn) {
        forgotPasswordBtn.addEventListener('click', function(e) {
            e.preventDefault();
            forgotPasswordModal.classList.add('active');
            resetEmailInput.focus();
        });
    }
    
    if (cancelResetBtn) {
        cancelResetBtn.addEventListener('click', function() {
            forgotPasswordModal.classList.remove('active');
            resetEmailInput.value = '';
            forgotPasswordError.textContent = '';
        });
    }
    
    if (sendResetBtn) {
        sendResetBtn.addEventListener('click', function() {
            const email = resetEmailInput.value.trim();
            
            if (!email || !validateEmail(email)) {
                forgotPasswordError.textContent = 'Please enter a valid email address';
                forgotPasswordError.className = 'error-message';
                return;
            }
            
            sendResetBtn.disabled = true;
            sendResetBtn.textContent = 'Sending...';
            
            const formData = new FormData();
            formData.append('email', email);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
            
            fetch('/accounts/forgot-password/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    forgotPasswordError.textContent = data.message || 'Reset link sent! Check your email.';
                    forgotPasswordError.className = 'success-message';
                    resetEmailInput.value = '';
                    
                    setTimeout(() => {
                        forgotPasswordModal.classList.remove('active');
                        forgotPasswordError.textContent = '';
                        sendResetBtn.disabled = false;
                        sendResetBtn.textContent = 'Send Reset Link';
                    }, 3000);
                } else {
                    forgotPasswordError.textContent = data.error || 'Failed to send reset link';
                    forgotPasswordError.className = 'error-message';
                    sendResetBtn.disabled = false;
                    sendResetBtn.textContent = 'Send Reset Link';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                forgotPasswordError.textContent = 'An error occurred. Please try again.';
                forgotPasswordError.className = 'error-message';
                sendResetBtn.disabled = false;
                sendResetBtn.textContent = 'Send Reset Link';
            });
        });
    }
});