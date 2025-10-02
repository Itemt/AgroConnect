document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('.add-to-cart-form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const url = this.action;
            const formData = new FormData(this);
            const csrfToken = this.querySelector('input[name="csrfmiddlewaretoken"]').value;

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                if (response.ok) {
                    // Reload the page to show the updated cart count
                    window.location.reload();
                } else {
                    // Handle errors
                    alert('Error al añadir el producto al carrito');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al añadir el producto al carrito');
            });
        });
    });
});
