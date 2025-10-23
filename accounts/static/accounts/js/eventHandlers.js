//Validation functions

function validateEmail(email){
    let emailRegEx = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

    if(!emailRegEx.test(email)){
        return false;
    }
    return true;
}
function validateDateOfBirth(date){
    if(!date || date.trim() === ""){
        return false;
    }
    return true;
}

function validateName(name){
    let nameRegEx = /^[a-zA-Z]+$/;

    if(!nameRegEx.test(name)){
        return false;
    }
    return true;
}
/*
function validatePassword(password){
    let passwordRegEx = /^(?=.*[0-9])(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{6,}$/; ///^(?=.*[^a-zA-Z]).{6,}$/;

    if(!passwordRegEx.test(password)){
        return false;
    }
    return true;
}
*/
function validateSignup(event){
    const accountType = document.getElementById('account_type').value;
    const prefix = accountType === 'client' ? '#id_client-' : '#id_therapist-';
    
    let email = document.querySelector(prefix + "email");
    let name = document.querySelector(prefix + "first_name");
    let password = document.querySelector(prefix + "password1");
    let confirmPassword = document.querySelector(prefix + "password2");

    let formIsValid = true;

    //email validation
    const emailSpan = document.createElement("span");    
    emailSpan.classList.add("error-text"); 
    let emailErrorMessage = email.parentNode;

    if(!validateEmail(email.value)){
        email.classList.add("error-box");
        emailSpan.innerHTML = "Invalid email format";
        if(emailErrorMessage.lastChild.innerHTML != emailSpan.innerHTML){ //used to only print error message once
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

    //date of birth validation
    const dateOfBirthSpan = document.createElement("span");    
    dateOfBirthSpan.classList.add("error-text");
    let dateOfBirth = document.querySelector(prefix + "date_of_birth");

    if(dateOfBirth){
        let dateOfBirthErrorMessage = dateOfBirth.parentNode;
        
        if(!validateDateOfBirth(dateOfBirth.value)){
            dateOfBirth.classList.add("error-box");
            dateOfBirthSpan.innerHTML = "Date of birth is required";
            if(dateOfBirthErrorMessage.lastChild.innerHTML != dateOfBirthSpan.innerHTML){
                dateOfBirthErrorMessage.appendChild(dateOfBirthSpan);
            }
            formIsValid = false;
        }
        else{
            dateOfBirth.classList.remove("error-box");
            if(dateOfBirthErrorMessage.lastChild.innerHTML === dateOfBirthSpan.innerHTML){
                dateOfBirthErrorMessage.removeChild(dateOfBirthErrorMessage.lastChild);
            }
        }
    }
    //name validation
    const nameSpan = document.createElement("span");    
    nameSpan.classList.add("error-text"); 
    let nameErrorMessage = name.parentNode;

    if(!validateName(name.value)){
        name.classList.add("error-box");
        nameSpan.innerHTML = "Invalid name";
        if(nameErrorMessage.lastChild.innerHTML != nameSpan.innerHTML){ //used to only print error message once
            nameErrorMessage.appendChild(nameSpan);  
        }
        formIsValid = false;
    }
    else{
        name.classList.remove("error-box");
        if(nameErrorMessage.lastChild.innerHTML === nameSpan.innerHTML){
            nameErrorMessage.removeChild(nameErrorMessage.lastChild);
        }
    }
    //password validation
    const passwordSpan = document.createElement("span");    
    passwordSpan.classList.add("error-text"); 
    let passwordErrorMessage = password.parentNode;

    const hasLength = /.{6,}/.test(password.value);
    const hasNumber = /\d/.test(password.value);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password.value);

    if(!hasLength || !hasNumber || !hasSpecial){
        password.classList.add("error-box");
        passwordSpan.innerHTML = "Password must be at least 6 characters, contain a special character and a number";
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

    //confirm password validation
    const confirmPasswordSpan = document.createElement("span");    
    confirmPasswordSpan.classList.add("error-text"); 
    let confirmPasswordErrorMessage = confirmPassword.parentNode;

	if(password.value != confirmPassword.value){
        confirmPassword.classList.add("error-box");
        confirmPasswordSpan.innerHTML = "Passwords do not match";
        if(confirmPasswordErrorMessage.lastChild.innerHTML != confirmPasswordSpan.innerHTML){ //used to only print error message once
            confirmPasswordErrorMessage.appendChild(confirmPasswordSpan);
        }
        formIsValid = false;
    }
    else{
        confirmPassword.classList.remove("error-box");
        if(confirmPasswordErrorMessage.lastChild.innerHTML === confirmPasswordSpan.innerHTML){
            confirmPasswordErrorMessage.removeChild(confirmPasswordErrorMessage.lastChild);
        }
	}
    
    if (formIsValid === false){
		event.preventDefault();
    }
}

function validateLogin(event){
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

    // Simplified password validation for login (just check if not empty)
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
        event.preventDefault();
    }
}
//start handler functions

function emailHandler(event){
    let email = event.target;

    const span = document.createElement("span"); 
    span.innerHTML = "Invalid email format";   
    span.classList.add("error-text");            
    
    let errorMessage = email.parentNode;

    if(!validateEmail(email.value)){
        email.classList.add("error-box");
        if(errorMessage.lastChild.innerHTML != span.innerHTML){ //used to only print error message once
            errorMessage.appendChild(span);
        }
    }
    else{
        email.classList.remove("error-box");
        if(errorMessage.lastChild.innerHTML === span.innerHTML){
            errorMessage.removeChild(errorMessage.lastChild);
        }
    }
}

function dateOfBirthHandler(event){
    let dateField = event.target;

    const span = document.createElement("span"); 
    span.innerHTML = "Date of birth is required";   
    span.classList.add("error-text");            
    
    let errorMessage = dateField.parentNode;

    if(!validateDateOfBirth(dateField.value)){
        dateField.classList.add("error-box");
        if(errorMessage.lastChild.innerHTML != span.innerHTML){
            errorMessage.appendChild(span);
        }
    }
    else{
        dateField.classList.remove("error-box");
        if(errorMessage.lastChild.innerHTML === span.innerHTML){
            errorMessage.removeChild(errorMessage.lastChild);
        }
    }
}

function validatePassword(password, checklist) {
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
function confirmPasswordHandler(passwordSelector) {
    return function(event) {
        let password = document.querySelector(passwordSelector);
        let confirmPassword = event.target;

        const span = document.createElement("span"); 
        span.innerHTML = "Passwords do not match";   
        span.classList.add("error-text"); 

        let errorMessage = confirmPassword.parentNode;

        if(password.value != confirmPassword.value){
            confirmPassword.classList.add("error-box");
            if(errorMessage.lastChild.innerHTML != span.innerHTML){
                errorMessage.appendChild(span);
            }
        }
        else{
            confirmPassword.classList.remove("error-box");
            if(errorMessage.lastChild.innerHTML === span.innerHTML){
                errorMessage.removeChild(errorMessage.lastChild);
            }
        }
    };
}

function nameHandler(event){
    let name = event.target;

    const span = document.createElement("span"); 
    span.innerHTML = "Invalid name";   
    span.classList.add("error-text");            
    
    let errorMessage = name.parentNode;

    if(!validateName(name.value)){
        name.classList.add("error-box");
        if(errorMessage.lastChild.innerHTML != span.innerHTML){ //used to only print error message once
            errorMessage.appendChild(span);
        }
    }
    else{
        name.classList.remove("error-box");
        if(errorMessage.lastChild.innerHTML === span.innerHTML){
            errorMessage.removeChild(errorMessage.lastChild);
        }
    }
}