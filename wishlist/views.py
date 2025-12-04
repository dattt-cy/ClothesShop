from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from .models import WishlistItem
from store.models import Product
from carts.models import Cart, CartItem


def wishlist(request):
    """Display user's wishlist"""
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        wishlist_items = WishlistItem.objects.filter(session_key=session_key).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_items.count(),
    }
    return render(request, 'wishlist/wishlist.html', context)


def add_to_wishlist(request, product_id):
    """Add product to wishlist via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user,
            product=product
        )
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        wishlist_item, created = WishlistItem.objects.get_or_create(
            session_key=session_key,
            product=product
        )
    
    # Count total wishlist items
    if request.user.is_authenticated:
        count = WishlistItem.objects.filter(user=request.user).count()
    else:
        count = WishlistItem.objects.filter(session_key=session_key).count()
    
    if created:
        return JsonResponse({
            'status': 'added',
            'message': _('Product added to wishlist!'),
            'wishlist_count': count
        })
    else:
        return JsonResponse({
            'status': 'exists',
            'message': _('Product already in wishlist!'),
            'wishlist_count': count
        })


def remove_from_wishlist(request, product_id):
    """Remove product from wishlist via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        WishlistItem.objects.filter(user=request.user, product=product).delete()
        count = WishlistItem.objects.filter(user=request.user).count()
    else:
        session_key = request.session.session_key
        if session_key:
            WishlistItem.objects.filter(session_key=session_key, product=product).delete()
            count = WishlistItem.objects.filter(session_key=session_key).count()
        else:
            count = 0
    
    return JsonResponse({
        'status': 'removed',
        'message': _('Product removed from wishlist!'),
        'wishlist_count': count
    })


def move_to_cart(request, product_id):
    """Move product from wishlist to cart"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        # Get or create cart
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, product=product)
            if cart_items.exists():
                messages.info(request, _('Product already in cart!'))
            else:
                CartItem.objects.create(user=request.user, product=product, quantity=1)
                messages.success(request, _('Product moved to cart!'))
            
            # Remove from wishlist
            WishlistItem.objects.filter(user=request.user, product=product).delete()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            cart, created = Cart.objects.get_or_create(cart_id=session_key)
            cart_items = CartItem.objects.filter(cart=cart, product=product)
            
            if cart_items.exists():
                messages.info(request, _('Product already in cart!'))
            else:
                CartItem.objects.create(cart=cart, product=product, quantity=1)
                messages.success(request, _('Product moved to cart!'))
            
            # Remove from wishlist
            WishlistItem.objects.filter(session_key=session_key, product=product).delete()
            
    except Exception as e:
        messages.error(request, _('An error occurred. Please try again.'))
    
    return redirect('wishlist')


def clear_wishlist(request):
    """Clear all items from wishlist"""
    if request.user.is_authenticated:
        WishlistItem.objects.filter(user=request.user).delete()
    else:
        session_key = request.session.session_key
        if session_key:
            WishlistItem.objects.filter(session_key=session_key).delete()
    
    messages.success(request, _('Wishlist cleared!'))
    return redirect('wishlist')
