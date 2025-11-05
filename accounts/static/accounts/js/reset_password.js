// Password validation
    const passwordInput = document.getElementById('id_password');
    const checklist = document.querySelector('.password-checklist');
    
    if (passwordInput && checklist) {
        passwordInput.addEventListener('input', function() {
            validatePasswordReset(this.value, checklist);
        });
    }
    
    function validatePasswordReset(password, checklist) {
        const requirements = [
            { className: 'length-check', regex: /.{6,}/ },
            { className: 'number-check', regex: /\d/ },
            { className: 'special-check', regex: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/ }
        ];
        
        requirements.forEach(function(req) {
            const element = checklist.querySelector('.' + req.className);
            if (req.regex.test(password)) {
                element.classList.add('valid');
            } else {
                element.classList.remove('valid');
            }
        });
    }