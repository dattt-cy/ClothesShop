// Wishlist functionality
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize wishlist state (will be called from template with product IDs)
window.initWishlist = function(wishlistProductIds) {
    wishlistProductIds.forEach(productId => {
        const button = document.querySelector(`.wishlist-toggle[data-product-id="${productId}"]`);
        if (button) {
            const icon = button.querySelector('i');
            icon.classList.remove('fa-heart-o');
            icon.classList.add('fa-heart');
            button.classList.add('in-wishlist');
        }
    });
};

// Toggle wishlist
document.addEventListener('DOMContentLoaded', function() {
    console.log('Wishlist script loaded');
    
    // Get wishlist product IDs from data attribute
    const wishlistData = document.getElementById('wishlist-data');
    if (wishlistData) {
        try {
            const wishlistProductIds = JSON.parse(wishlistData.dataset.wishlistIds || '[]');
            console.log('Wishlist product IDs:', wishlistProductIds);
            
            // Mark products already in wishlist
            wishlistProductIds.forEach(productId => {
                const button = document.querySelector(`.wishlist-toggle[data-product-id="${productId}"]`);
                if (button) {
                    const icon = button.querySelector('i');
                    icon.classList.remove('fa-heart-o');
                    icon.classList.add('fa-heart');
                    button.classList.add('in-wishlist');
                }
            });
        } catch (e) {
            console.error('Error parsing wishlist data:', e);
        }
    }
    
    // Add event listeners to all wishlist buttons
    document.querySelectorAll('.wishlist-toggle').forEach(button => {
        console.log('Found wishlist button:', button.dataset.productId);
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const productId = this.dataset.productId;
            const icon = this.querySelector('i');
            const isInWishlist = icon.classList.contains('fa-heart');
            
            // Get current language code from URL
            const currentPath = window.location.pathname;
            const langMatch = currentPath.match(/^\/(en|vi|ja)\//);
            const langPrefix = langMatch ? '/' + langMatch[1] : '';
            
            const url = isInWishlist 
                ? `${langPrefix}/wishlist/remove/${productId}/`
                : `${langPrefix}/wishlist/add/${productId}/`;
            
            console.log('Toggling wishlist for product:', productId, 'URL:', url);
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                
                // Toggle icon
                if (data.status === 'added' || data.status === 'exists') {
                    icon.classList.remove('fa-heart-o');
                    icon.classList.add('fa-heart');
                    this.classList.add('in-wishlist');
                } else if (data.status === 'removed') {
                    icon.classList.remove('fa-heart');
                    icon.classList.add('fa-heart-o');
                    this.classList.remove('in-wishlist');
                }
                
                // Animate
                this.classList.add('animate');
                setTimeout(() => this.classList.remove('animate'), 600);
                
                // Update counter
                const counterBadge = document.querySelector('.wishlist-counter');
                if (counterBadge) {
                    counterBadge.textContent = data.wishlist_count;
                    if (data.wishlist_count > 0) {
                        counterBadge.style.display = 'inline-block';
                    } else {
                        counterBadge.style.display = 'none';
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
