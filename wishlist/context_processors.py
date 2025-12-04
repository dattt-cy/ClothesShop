from .models import WishlistItem
import json


def wishlist_counter(request):
    """Context processor to add wishlist count to all templates"""
    wishlist_count = 0
    wishlist_items = []
    wishlist_product_ids = []
    
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user)
        wishlist_count = wishlist_items.count()
        wishlist_product_ids = list(wishlist_items.values_list('product_id', flat=True))
    else:
        session_key = request.session.session_key
        if session_key:
            wishlist_items = WishlistItem.objects.filter(session_key=session_key)
            wishlist_count = wishlist_items.count()
            wishlist_product_ids = list(wishlist_items.values_list('product_id', flat=True))
    
    return {
        'wishlist_count': wishlist_count,
        'wishlist_items_context': wishlist_items,
        'wishlist_product_ids_json': json.dumps(wishlist_product_ids),
    }
