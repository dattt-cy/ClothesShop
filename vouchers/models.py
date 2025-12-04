from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Voucher(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('freeship', 'Free Shipping'),
    ]
    
    code = models.CharField(max_length=50, unique=True, help_text="Mã voucher (VD: NEWUSER2025)")
    description = models.TextField(help_text="Mô tả voucher")
    
    # Loại và giá trị giảm giá
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Giá trị giảm (% hoặc số tiền)"
    )
    
    # Điều kiện áp dụng
    min_purchase = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Đơn hàng tối thiểu để áp dụng voucher"
    )
    max_discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Giảm tối đa (chỉ cho % discount)"
    )
    
    # Số lượng
    total_quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Tổng số lượng voucher (0 = không giới hạn)"
    )
    used_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Giới hạn sử dụng
    per_user_limit = models.IntegerField(
        default=1,
        validators=[MinValueValidator(0)],
        help_text="Số lần mỗi user có thể dùng (0 = không giới hạn)"
    )
    
    # Thời gian hiệu lực
    start_date = models.DateTimeField(help_text="Ngày bắt đầu có hiệu lực")
    end_date = models.DateTimeField(help_text="Ngày hết hạn")
    
    # Trạng thái
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_display()}"
    
    def get_discount_display(self):
        """Hiển thị giá trị giảm giá dễ đọc"""
        if self.discount_type == 'percentage':
            return f"{self.discount_value}% OFF"
        elif self.discount_type == 'fixed':
            return f"${self.discount_value:,.2f} OFF"
        else:
            return "FREE SHIPPING"
    
    def is_valid(self):
        """Kiểm tra voucher còn hiệu lực không"""
        now = timezone.now()
        if not self.is_active:
            return False, "Voucher không còn hoạt động"
        if now < self.start_date:
            return False, "Voucher chưa đến thời gian áp dụng"
        if now > self.end_date:
            return False, "Voucher đã hết hạn"
        if self.total_quantity > 0 and self.used_quantity >= self.total_quantity:
            return False, "Voucher đã hết lượt sử dụng"
        return True, "Voucher hợp lệ"
    
    def can_user_use(self, user):
        """Kiểm tra user có thể dùng voucher này không"""
        if self.per_user_limit == 0:
            return True, "OK"
        
        usage_count = VoucherUsage.objects.filter(
            voucher=self,
            user=user
        ).count()
        
        if usage_count >= self.per_user_limit:
            return False, f"Bạn đã sử dụng voucher này {usage_count} lần (tối đa {self.per_user_limit} lần)"
        return True, "OK"
    
    def calculate_discount(self, order_total):
        """Tính toán số tiền giảm"""
        if self.discount_type == 'percentage':
            discount = order_total * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        elif self.discount_type == 'fixed':
            return min(self.discount_value, order_total)
        elif self.discount_type == 'freeship':
            return 0  # Shipping sẽ được xử lý riêng
        return 0
    
    @property
    def remaining_quantity(self):
        """Số lượng còn lại"""
        if self.total_quantity == 0:
            return "Unlimited"
        return self.total_quantity - self.used_quantity
    
    @property
    def usage_percentage(self):
        """Phần trăm đã sử dụng"""
        if self.total_quantity == 0:
            return 0
        return (self.used_quantity / self.total_quantity) * 100


class VoucherUsage(models.Model):
    """Lưu lịch sử sử dụng voucher"""
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, null=True, blank=True)
    
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-used_at']
        verbose_name = 'Voucher Usage'
        verbose_name_plural = 'Voucher Usages'
    
    def __str__(self):
        return f"{self.user.email} used {self.voucher.code}"


class UserVoucher(models.Model):
    """Voucher mà user đã thu thập/lưu"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_vouchers')
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    
    collected_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'voucher']
        ordering = ['-collected_at']
        verbose_name = 'User Voucher'
        verbose_name_plural = 'User Vouchers'
    
    def __str__(self):
        return f"{self.user.email} - {self.voucher.code}"
