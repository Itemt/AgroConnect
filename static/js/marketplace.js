// Carousels state
const carousels = {};

// Initialize carousel for a publication
function initCarousel(publicationId) {
    if (!carousels[publicationId]) {
        carousels[publicationId] = {
            currentIndex: 0,
            container: document.querySelector(`[data-publication-id="${publicationId}"]`),
            track: null,
            slides: [],
            dots: []
        };
        
        const carousel = carousels[publicationId];
        if (!carousel.container) return;
        
        carousel.track = carousel.container.querySelector('.carousel-track');
        carousel.slides = carousel.container.querySelectorAll('.carousel-slide');
        carousel.dots = carousel.container.querySelectorAll('.carousel-dot');
    }
}

// Navigate carousel
function carouselNext(publicationId) {
    initCarousel(publicationId);
    const carousel = carousels[publicationId];
    if (!carousel || !carousel.slides.length) return;
    
    carousel.currentIndex = (carousel.currentIndex + 1) % carousel.slides.length;
    updateCarousel(publicationId);
}

function carouselPrev(publicationId) {
    initCarousel(publicationId);
    const carousel = carousels[publicationId];
    if (!carousel || !carousel.slides.length) return;
    
    carousel.currentIndex = (carousel.currentIndex - 1 + carousel.slides.length) % carousel.slides.length;
    updateCarousel(publicationId);
}

function updateCarousel(publicationId) {
    const carousel = carousels[publicationId];
    if (!carousel) return;
    
    // Update track position
    const offset = -carousel.currentIndex * 100;
    carousel.track.style.transform = `translateX(${offset}%)`;
    
    // Update dots
    carousel.dots.forEach((dot, index) => {
        if (index === carousel.currentIndex) {
            dot.classList.add('!bg-white', '!w-6');
            dot.classList.remove('bg-white/60');
        } else {
            dot.classList.remove('!bg-white', '!w-6');
            dot.classList.add('bg-white/60');
        }
    });
}

// Initialize all carousels on page load
document.addEventListener('DOMContentLoaded', function () {
    // Initialize carousels
    document.querySelectorAll('.carousel-container').forEach(container => {
        const publicationId = container.getAttribute('data-publication-id');
        if (publicationId) {
            initCarousel(publicationId);
        }
    });
    
    // Add to cart forms
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
