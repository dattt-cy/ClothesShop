from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    """Add product to cart, merging items with same variation set."""
    product = get_object_or_404(Product, id=product_id)
    product_variation = []

    if request.method == "POST":
        for key, value in request.POST.items():
            # Skip csrf token
            if key in ["color", "size"]:
                try:
                    variation = Variation.objects.get(
                        product=product,
                        variation_category__iexact=key,
                        variation_value__iexact=value,
                        is_active=True,
                    )
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

    cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

    cart_items = CartItem.objects.filter(product=product, cart=cart)

    if cart_items.exists():
        # Build list of existing variation sets
        existing_variation_sets = []
        id_map = []
        for item in cart_items:
            existing_variation_sets.append(list(item.variations.all()))
            id_map.append(item.id)

        matched = False
        if product_variation:
            for index, existing in enumerate(existing_variation_sets):
                if set(existing) == set(product_variation):
                    cart_item = CartItem.objects.get(id=id_map[index])
                    cart_item.quantity += 1
                    cart_item.save()
                    matched = True
                    break
        else:  # No variation selected; treat as single item bucket
            cart_item = cart_items.first()
            cart_item.quantity += 1
            cart_item.save()
            matched = True

        if not matched:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()
    else:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        if product_variation:
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id =_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if (cart_item.quantity > 1):
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total ) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
       pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax'        : tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html', context)

