from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.crypto import get_random_string
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def _finalize_order(request, order, payment):
    """Internal helper: move cart items to OrderProduct, reduce stock, clear cart, send email."""
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        op = OrderProduct.objects.create(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
        )
        op.variations.set(item.variations.all())
        # reduce stock
        product = item.product
        product.stock -= item.quantity
        product.save()
    
    # Lưu voucher usage nếu có
    if 'voucher_code' in request.session and 'voucher_discount' in request.session:
        from vouchers.models import Voucher, VoucherUsage
        try:
            voucher = Voucher.objects.get(code=request.session['voucher_code'])
            voucher_discount = float(request.session['voucher_discount'])
            
            # Tạo voucher usage record
            VoucherUsage.objects.create(
                voucher=voucher,
                user=request.user,
                order=order,
                discount_amount=voucher_discount,
                order_total=order.order_total
            )
            
            # Tăng used_quantity
            voucher.used_quantity += 1
            voucher.save()
            
            # Xóa voucher khỏi session
            del request.session['voucher_code']
            del request.session['voucher_discount']
            
        except Voucher.DoesNotExist:
            pass
    
    cart_items.delete()
    # send email
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    EmailMessage(mail_subject, message, to=[request.user.email]).send()


@login_required
def payments(request):
    """Existing JSON-based payment endpoint (e.g. PayPal)"""
    body = json.loads(request.body)
    order = get_object_or_404(Order, user=request.user, is_ordered=False, order_number=body['orderID'])
    payment = Payment.objects.create(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    order.payment = payment
    order.is_ordered = True
    order.save()
    _finalize_order(request, order, payment)
    return JsonResponse({'order_number': order.order_number, 'transID': payment.payment_id})


@login_required
def cod_payment(request, order_number):
    """Finalize order via COD.
    - Nếu order đã is_ordered: chuyển thẳng sang chi tiết.
    - Nếu chưa: tạo payment COD và finalize.
    - Nếu không thuộc user: 404.
    """
    try:
        order = Order.objects.get(user=request.user, order_number=order_number)
    except Order.DoesNotExist:
        # Giữ 404 chuẩn để tránh lộ order người khác
        raise

    if order.is_ordered:
        messages.info(request, 'Đơn hàng đã được hoàn tất trước đó.')
        return redirect('order_detail', order_id=order.order_number)

    payment = Payment.objects.create(
        user=request.user,
        payment_id='COD-' + get_random_string(10),
        payment_method='COD',
        amount_paid=order.order_total,
        status='PENDING',
    )
    order.payment = payment
    order.is_ordered = True
    order.save()
    _finalize_order(request, order, payment)
    messages.success(request, 'Đơn hàng COD đã được ghi nhận.')
    return redirect('order_detail', order_id=order.order_number)

def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    voucher_discount = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    
    # Áp dụng voucher discount nếu có
    if 'voucher_discount' in request.session:
        voucher_discount = float(request.session['voucher_discount'])
    
    # Tính toán sau khi trừ voucher
    discounted_total = max(0, total - voucher_discount)
    tax = (2 * discounted_total) / 100
    grand_total = discounted_total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
            # Lưu voucher info nếu có
            if 'voucher_code' in request.session:
                data.voucher_code = request.session.get('voucher_code')
                data.voucher_discount = voucher_discount
            
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'voucher_discount': voucher_discount,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')