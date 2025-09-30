
document.addEventListener('DOMContentLoaded', function() {
    // Function to update cities based on selected department
    function updateCities(deptSelect, citySelect) {
        if (!deptSelect || !citySelect) return;

        const selectedDepartment = deptSelect.value;
        // Get the URL from the data attribute of the department select element
        const url = deptSelect.dataset.citiesUrl;

        if (selectedDepartment && url) {
            fetch(`${url}?department=${encodeURIComponent(selectedDepartment)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    citySelect.innerHTML = '<option value="">Selecciona una ciudad</option>';
                    if (data.success && data.cities) {
                        data.cities.forEach(city => {
                            const option = document.createElement('option');
                            option.value = city; // The view returns a list of strings
                            option.textContent = city;
                            citySelect.appendChild(option);
                        });
                    }
                    citySelect.disabled = false;
                })
                .catch(error => {
                    console.error('Error loading cities:', error);
                    citySelect.innerHTML = '<option value="">Error al cargar ciudades</option>';
                    citySelect.disabled = true;
                });
        } else {
            citySelect.innerHTML = '<option value="">Selecciona primero un departamento</option>';
            citySelect.disabled = true;
        }
    }

    // Generic handler for all dependent dropdowns
    function setupDependentDropdown(departmentId, cityId) {
        const deptSelect = document.getElementById(departmentId);
        const citySelect = document.getElementById(cityId);

        if (deptSelect && citySelect) {
            // Disable city select initially if no department is selected
            if (!deptSelect.value) {
                citySelect.disabled = true;
            }

            deptSelect.addEventListener('change', function() {
                updateCities(deptSelect, citySelect);
            });

            // If a department is already selected on page load (e.g., form validation error), trigger the update
            if (deptSelect.value) {
                updateCities(deptSelect, citySelect);
            }
        }
    }

    // Setup for Registration Form
    setupDependentDropdown('id_departamento', 'id_ciudad');

    // Setup for Producer Profile Form
    setupDependentDropdown('id_departamento_producer', 'id_ciudad_producer');

    // Setup for Buyer Profile Form
    setupDependentDropdown('id_departamento_buyer', 'id_ciudad_buyer');

    // Marketplace Filters Toggle
    const toggleBtn = document.getElementById('toggle-filters-btn');
    const filtersContainer = document.getElementById('filters-container');

    if (toggleBtn && filtersContainer) {
        toggleBtn.addEventListener('click', function () {
            filtersContainer.classList.toggle('hidden');
            const isHidden = filtersContainer.classList.contains('hidden');
            if (isHidden) {
                toggleBtn.innerHTML = '<i class="fas fa-filter"></i>';
            } else {
                toggleBtn.innerHTML = '<i class="fas fa-times"></i>';
            }
        });
    }

    // Cancel Order
    const checkbox = document.getElementById('confirm-cancellation');
    const button = document.getElementById('cancel-button');

    if (checkbox && button) {
        checkbox.addEventListener('change', function() {
            button.disabled = !this.checked;
        });
    }

    // Conversation Detail
    const messageList = document.getElementById('message-list');
    if (messageList) {
        messageList.scrollTop = messageList.scrollHeight;
    }

    const contentField = document.querySelector('[name="content"]');
    if (contentField) {
        contentField.className = 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 transition-colors';
        contentField.placeholder = 'Escribe tu mensaje aquí...';
    }

    // Apply styles to all form fields with .field-wrapper
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const fields = form.querySelectorAll('.field-wrapper > div > *');
        fields.forEach(field => {
            let classList = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm';
            if (field.tagName.toLowerCase() === 'textarea') {
                classList += ' h-32';
            }
            if (field.type === 'checkbox') {
                classList = 'h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500';
            }
            field.className = classList;
        });
    });

    // Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarTexts = document.querySelectorAll('.sidebar-text');

    if (sidebar && mainContent && sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('w-64');
            sidebar.classList.toggle('w-20');
            mainContent.classList.toggle('ml-64');
            mainContent.classList.toggle('ml-20');
            sidebarTexts.forEach(text => {
                text.classList.toggle('hidden');
            });
        });
    }

    // The old registration logic is now handled by the generic setupDependentDropdown
});
