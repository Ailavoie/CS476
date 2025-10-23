document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const clientForm = document.getElementById('client-form');
    const therapistForm = document.getElementById('therapist-form');
    const accountTypeInput = document.getElementById('account_type');
    const formTitle = document.getElementById('form-title');
    const registerContainer = document.querySelector('.register-container');

    // CRITICAL: Variable Definitions for Country/Province
    const clientCountry = document.getElementById('id_client-country');
    const clientProvince = document.getElementById('id_client-province');
    const therapistCountry = document.getElementById('id_therapist-country');
    const therapistProvince = document.getElementById('id_therapist-province');

    // Select2 Target
    const specialtySelect = document.querySelector('.multi-select-specialty');

    // Get the initial tab from the server (defaults to 'client' on first load)
    const initialTab = registerContainer ? registerContainer.dataset.initialTab || 'client' : 'client';

    function disableFields(container, disabled) {
        if (container) {
            container.querySelectorAll('input, select, textarea').forEach(el => {
                el.disabled = disabled;
            });
        }
    }

    function toggleTab(tab) {
        tabButtons.forEach(btn => btn.classList.remove('active'));
        const targetButton = document.querySelector(`.tab-button[data-tab="${tab}"]`);
        if (targetButton) {
            targetButton.classList.add('active');
        }

        if (clientForm) clientForm.classList.remove('active');
        if (therapistForm) therapistForm.classList.remove('active');

        disableFields(clientForm, true);
        disableFields(therapistForm, true);

        if (tab === 'client' && clientForm && accountTypeInput && formTitle) {
            clientForm.classList.add('active');
            accountTypeInput.value = 'client';
            disableFields(clientForm, false);
            formTitle.textContent = "Register as a Client";
        } else if (tab === 'therapist' && therapistForm && accountTypeInput && formTitle) {
            therapistForm.classList.add('active');
            accountTypeInput.value = 'therapist';
            disableFields(therapistForm, false);
            formTitle.textContent = "Register as a Therapist";
        }
    }

    if (tabButtons.length > 0) {
        toggleTab('client');

        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                toggleTab(this.dataset.tab);
            });
        });
    }
    // ------------------------------------------------------------------
    // Function to load provinces via AJAX 
    // ------------------------------------------------------------------
    function loadProvinces(countrySelect, provinceSelect) {
        if (!countrySelect || !provinceSelect) {
            console.error("loadProvinces called, but country or province element is missing.");
            return;
        }

        const countryCode = countrySelect.value;
        const url = `/accounts/ajax/load_provinces/?country=${countryCode}`; 

        console.log(`loadProvinces function called. Country Code: ${countryCode}`);
        
        provinceSelect.innerHTML = '';
        
        let defaultOption = document.createElement('option');
        defaultOption.value = '';
        
        if (countryCode) {
            defaultOption.textContent = 'Loading...';
        } else {
            defaultOption.textContent = 'Select Country First';
        }
        provinceSelect.appendChild(defaultOption);

        if (!countryCode) {
            provinceSelect.disabled = true;
            return;
        }
        
        provinceSelect.disabled = true;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                provinceSelect.innerHTML = ''; 
                
                let placeholderOption = document.createElement('option');
                placeholderOption.value = '';
                placeholderOption.textContent = 'Select State/Province';
                provinceSelect.appendChild(placeholderOption);

                data.forEach(([code, name]) => {
                    let option = document.createElement('option');
                    option.value = code;
                    option.textContent = name;
                    provinceSelect.appendChild(option);
                });
                provinceSelect.disabled = false;
            })
            .catch(error => {
                console.error('Final Error Catch (Network/Parsing):', error);
                provinceSelect.innerHTML = '';
                let errorOption = document.createElement('option');
                errorOption.value = '';
                errorOption.textContent = 'Error loading regions';
                provinceSelect.appendChild(errorOption);
                provinceSelect.disabled = true;
            });
    }

    // ------------------------------------------------------------------
    // 1. Initialize Searchable Select2 Field
    // ------------------------------------------------------------------
    if (specialtySelect && typeof jQuery !== 'undefined' && $(specialtySelect).select2) {
        $(specialtySelect).select2({
            placeholder: "Select one or more specialties",
            allowClear: true,
            width: '100%'
        });
    }


    // ------------------------------------------------------------------
    // 2. Attach Click Listeners to Tab Buttons
    // ------------------------------------------------------------------
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            toggleTab(tabName);
        });
    });

    // ------------------------------------------------------------------
    // 3. Attach Country/Province Listeners
    // ------------------------------------------------------------------
    if (clientCountry && clientProvince) { 
        clientCountry.addEventListener('change', () => loadProvinces(clientCountry, clientProvince));
        loadProvinces(clientCountry, clientProvince); 
    }
    
    if (therapistCountry && therapistProvince) {
        therapistCountry.addEventListener('change', () => loadProvinces(therapistCountry, therapistProvince));
        loadProvinces(therapistCountry, therapistProvince); 
    }

    // Initialize the tab
    toggleTab(initialTab);

    // ------------------------------------------------------------------
    // Final Focus Logic (Handles "Not Focusable" warnings)
    // ------------------------------------------------------------------
    const activeFormId = initialTab === 'client' ? 'client-form' : 'therapist-form';
    const activeForm = document.getElementById(activeFormId);

    if (activeForm) {
        // Find the first form group element that contains the 'has-error' class
        // (Requires the 'has-error' class to be added to the form-group div in register.html)
        const firstErrorGroup = activeForm.querySelector('.form-group.has-error');
        
        if (firstErrorGroup) {
            // Find the actual input/select element within that error group
            const firstInput = firstErrorGroup.querySelector('input:not([type="hidden"]):not([type="submit"]), select, textarea');
            
            if (firstInput) {
                // Use a slight delay to ensure the form is fully visible
                setTimeout(() => {
                    firstInput.focus();
                    firstInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 50); 
            }
        }
    }
    // Email validation
    const clientEmail = document.querySelector("#id_client-email");
    const therapistEmail = document.querySelector("#id_therapist-email");
    
    if (clientEmail) {
        clientEmail.addEventListener("blur", emailHandler); 
    }
    
    if (therapistEmail) {
        therapistEmail.addEventListener("blur", emailHandler); 
    }

    // Date of birth validation
    const clientDOB = document.querySelector("#id_client-date_of_birth");
    const therapistDOB = document.querySelector("#id_therapist-date_of_birth");

    if (clientDOB) {
        clientDOB.addEventListener("blur", dateOfBirthHandler); 
    }

    if (therapistDOB) {
        therapistDOB.addEventListener("blur", dateOfBirthHandler); 
    }

    // Confirm password validation
    const clientConfirmPassword = document.querySelector("#id_client-password2");
    const therapistConfirmPassword = document.querySelector("#id_therapist-password2");
    
    if (clientConfirmPassword) {
        clientConfirmPassword.addEventListener("blur", confirmPasswordHandler("#id_client-password1")); 
    }
    
    if (therapistConfirmPassword) {
        therapistConfirmPassword.addEventListener("blur", confirmPasswordHandler("#id_therapist-password1")); 
    }

    // Password Checklist Functionality
    const passwordFields = document.querySelectorAll('input[type="password"][name*="password1"]');
    
    if (passwordFields.length > 0) {
        passwordFields.forEach(function(passwordField) {
            const checklist = createPasswordChecklist();
            const formGroup = passwordField.closest('.form-group');
            if (formGroup) {
                formGroup.insertAdjacentElement('afterend', checklist);
                
                passwordField.addEventListener('focus', function() {
                    checklist.style.display = 'block';
                });
                
                passwordField.addEventListener('blur', function() {
                    checklist.style.display = 'none';
                });
                
                passwordField.addEventListener('input', function() {
                    validatePassword(passwordField.value, checklist);
                });
            }
        });
    }

    // Name validation
    const clientName = document.querySelector("#id_client-first_name");
    const therapistName = document.querySelector("#id_therapist-first_name");
    
    if (clientName) {
        clientName.addEventListener("blur", nameHandler); 
    }
    
    if (therapistName) {
        therapistName.addEventListener("blur", nameHandler); 
    }

    // Form submission validation
    const form = document.getElementById("signup-form");

    if (form) {
        
        const submitButton = form.querySelector('button[type="submit"]');
        
        if (submitButton) {
            submitButton.addEventListener("click", function(e) {
                const formEvent = {
                    preventDefault: function() {
                        e.preventDefault();
                    },
                    target: form
                };
                
                validateSignup(formEvent);
            });
        }
    } else {
        console.error("Form with id 'signup-form' NOT FOUND!");
    }
});

// Helper function for password checklist
function createPasswordChecklist() {
    const checklist = document.createElement('div');
    checklist.className = 'password-checklist';
    checklist.style.display = 'none';
    
    checklist.innerHTML = `
        <p class="checklist-title">Password Requirements:</p>
        <ul>
            <li class="requirement length-check">
                <span class="check-icon"></span>
                At least 6 characters
            </li>
            <li class="requirement number-check">
                <span class="check-icon"></span>
                Contains a number
            </li>
            <li class="requirement special-check">
                <span class="check-icon"></span>
                Contains a special character
            </li>
        </ul>
    `;
    
    return checklist;
}
