
document.addEventListener('DOMContentLoaded', function() {
    // Function to update cities based on selected department
    function updateCities(deptSelect, citySelect) {
        if (!deptSelect || !citySelect) return;

        const selectedDepartment = deptSelect.value;
        const url = deptSelect.dataset.citiesUrl;

        if (selectedDepartment && url) {
            fetch(`${url}?department=${encodeURIComponent(selectedDepartment)}`)
                .then(response => response.json())
                .then(data => {
                    citySelect.innerHTML = '<option value="">Selecciona una ciudad</option>';
                    if (data.success && data.cities) {
                        data.cities.forEach(city => {
                            const option = document.createElement('option');
                            option.value = city.value;
                            option.textContent = city.text;
                            citySelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error loading cities:', error);
                    citySelect.innerHTML = '<option value="">Error al cargar ciudades</option>';
                });
        } else {
            citySelect.innerHTML = '<option value="">Selecciona primero un departamento</option>';
        }
    }

    // Profile Edit
    const departamentoSelect = document.getElementById('id_departamento');
    const ciudadSelect = document.getElementById('id_ciudad');
    if (departamentoSelect && ciudadSelect) {
        departamentoSelect.addEventListener('change', function() {
            updateCities(departamentoSelect, ciudadSelect);
        });
    }

    const departamentoBuyerSelect = document.getElementById('id_departamento_buyer');
    const ciudadBuyerSelect = document.getElementById('id_ciudad_buyer');
    if (departamentoBuyerSelect && ciudadBuyerSelect) {
        departamentoBuyerSelect.addEventListener('change', function() {
            updateCities(departamentoBuyerSelect, ciudadBuyerSelect);
        });
    }

    // Crop Form
    const departamentoCropSelect = document.getElementById('id_departamento_crop');
    const ciudadCropSelect = document.getElementById('id_ciudad_crop');
    if (departamentoCropSelect && ciudadCropSelect) {
        departamentoCropSelect.addEventListener('change', function() {
            updateCities(departamentoCropSelect, ciudadCropSelect);
        });
    }

    // Marketplace
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

    // Registration form city loader
    const regDepartamentoSelect = document.querySelector('form[method="post"] #id_departamento');
    const regCiudadSelect = document.querySelector('form[method="post"] #id_ciudad');
    if (regDepartamentoSelect && regCiudadSelect) {
        regDepartamentoSelect.addEventListener('change', function() {
            updateCities(regDepartamentoSelect, regCiudadSelect);
        });
    }
});
