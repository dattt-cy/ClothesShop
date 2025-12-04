from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from .models import Voucher, UserVoucher, VoucherUsage
from decimal import Decimal

@login_required(login_url='login')
def voucher_list(request):
    """Hiển thị danh sách voucher khả dụng"""
    now = timezone.now()
    
    # Voucher đang hoạt động và còn hiệu lực
    available_vouchers = Voucher.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).exclude(
        total_quantity__gt=0,
        used_quantity__gte=models.F('total_quantity')
    )
    
    # Voucher đã lưu của user
    saved_vouchers = UserVoucher.objects.filter(
        user=request.user,
        is_used=False,
        voucher__is_active=True,
        voucher__end_date__gte=now
    ).select_related('voucher')
    
    context = {
        'available_vouchers': available_vouchers,
        'saved_vouchers': saved_vouchers,
    }
    return render(request, 'vouchers/voucher_list.html', context)


@login_required(login_url='login')
def collect_voucher(request, voucher_id):
    """Thu thập voucher vào My Vouchers"""
    voucher = get_object_or_404(Voucher, id=voucher_id)
    
    # Kiểm tra voucher còn hiệu lực
    is_valid, message = voucher.is_valid()
    if not is_valid:
        messages.error(request, message)
        return redirect('voucher_list')
    
    # Thêm vào My Vouchers
    user_voucher, created = UserVoucher.objects.get_or_create(
        user=request.user,
        voucher=voucher
    )
    
    if created:
        messages.success(request, f'Đã thêm voucher {voucher.code} vào My Vouchers!')
    else:
        messages.info(request, 'Bạn đã có voucher này rồi!')
    
    return redirect('voucher_list')


def apply_voucher(request):
    """AJAX: Áp dụng voucher vào giỏ hàng"""
    if request.method == 'POST':
        voucher_code = request.POST.get('voucher_code', '').strip().upper()
        
        if not voucher_code:
            return JsonResponse({
                'success': False,
                'message': 'Vui lòng nhập mã voucher'
            })
        
        try:
            voucher = Voucher.objects.get(code=voucher_code)
        except Voucher.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Mã voucher không tồn tại'
            })
        
        # Kiểm tra voucher hợp lệ
        is_valid, message = voucher.is_valid()
        if not is_valid:
            return JsonResponse({
                'success': False,
                'message': message
            })
        
        # Kiểm tra user có thể dùng không
        if request.user.is_authenticated:
            can_use, message = voucher.can_user_use(request.user)
            if not can_use:
                return JsonResponse({
                    'success': False,
                    'message': message
                })
        
        # Lấy tổng tiền từ cart
        from carts.models import Cart, CartItem
        
        cart_items = None
        total = 0
        
        # Kiểm tra user authenticated hoặc anonymous
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            # Anonymous user - dùng session cart
            try:
                cart = Cart.objects.get(cart_id=request.session.session_key)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            except Cart.DoesNotExist:
                pass
        
        if not cart_items or cart_items.count() == 0:
            return JsonResponse({
                'success': False,
                'message': 'Giỏ hàng trống'
            })
        
        # Tính tổng tiền
        for item in cart_items:
            total += item.sub_total()
        
        # Kiểm tra đơn tối thiểu
        if total < voucher.min_purchase:
            return JsonResponse({
                'success': False,
                'message': f'Đơn hàng tối thiểu ${voucher.min_purchase:,.2f} để sử dụng voucher này'
            })
        
        # Tính giảm giá
        discount = voucher.calculate_discount(total)
        
        # Lưu vào session
        request.session['voucher_code'] = voucher.code
        request.session['voucher_discount'] = float(discount)
        
        return JsonResponse({
            'success': True,
            'message': f'Áp dụng voucher thành công! Bạn được giảm ${discount:,.2f}',
            'discount': float(discount),
            'voucher_code': voucher.code,
            'discount_display': voucher.get_discount_display()
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    })


def remove_voucher(request):
    """AJAX: Xóa voucher khỏi giỏ hàng"""
    if 'voucher_code' in request.session:
        del request.session['voucher_code']
    if 'voucher_discount' in request.session:
        del request.session['voucher_discount']
    
    return JsonResponse({
        'success': True,
        'message': 'Đã xóa voucher'
    })
