// File: static/accounts/js/register.js

document.addEventListener('DOMContentLoaded', function() {
    // Variable Definitions
    const tabButtons = document.querySelectorAll('.tab-button');
    const registerContainer = document.querySelector('.register-container');
    const accountTypeInput = document.getElementById('account_type');
    const formTitle = document.getElementById('form-title');

    // CRITICAL: Variable Definitions for Country/Province
    const clientCountry = document.getElementById('id_client_country');
    const clientProvince = document.getElementById('id_client_province');
    const therapistCountry = document.getElementById('id_therapist_country');
    const therapistProvince = document.getElementById('id_therapist_province');
    
    // Select2 Target
    const specialtySelect = document.querySelector('.multi-select-specialty');

    // Get the initial tab from the server (defaults to 'client' on first load)
    const initialTab = registerContainer ? registerContainer.dataset.initialTab || 'client' : 'client';

    // ------------------------------------------------------------------
    // Function to handle tab switching (VISUAL-ONLY FIX for CSRF)
    // ------------------------------------------------------------------
    function toggleTab(tab) {
        // 1. Manage button appearance
        tabButtons.forEach(btn => btn.classList.remove('active'));
        const activeTabButton = document.querySelector(`.tab-button[data-tab="${tab}"]`);
        if (activeTabButton) {
            activeTabButton.classList.add('active');
        }

        const clientForm = document.getElementById('client-form');
        const therapistForm = document.getElementById('therapist-form');

        // 2. Hide all forms
        if (clientForm) clientForm.classList.remove('active');
        if (therapistForm) therapistForm.classList.remove('active');

        // 3. Show the active form
        if (tab === 'client' && clientForm) {
            clientForm.classList.add('active');
            if (accountTypeInput) accountTypeInput.value = 'client';
            if (formTitle) formTitle.textContent = "Register as a Client";

        } else if (tab === 'therapist' && therapistForm) {
            therapistForm.classList.add('active');
            if (accountTypeInput) accountTypeInput.value = 'therapist';
            if (formTitle) formTitle.textContent = "Register as a Therapist";
        }
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
});