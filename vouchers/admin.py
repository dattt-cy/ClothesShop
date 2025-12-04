from django.contrib import admin
from .models import Voucher, VoucherUsage, UserVoucher

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = [
        'code', 
        'discount_type', 
        'discount_value', 
        'min_purchase',
        'used_quantity',
        'total_quantity',
        'remaining_display',
        'start_date', 
        'end_date', 
        'is_active',
        'status_display'
    ]
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['code', 'description']
    readonly_fields = ['used_quantity', 'created_at', 'updated_at', 'usage_percentage']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Giảm giá', {
            'fields': ('discount_type', 'discount_value', 'max_discount')
        }),
        ('Điều kiện', {
            'fields': ('min_purchase', 'total_quantity', 'used_quantity', 'per_user_limit')
        }),
        ('Thời gian', {
            'fields': ('start_date', 'end_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'usage_percentage'),
            'classes': ('collapse',)
        }),
    )
    
    def remaining_display(self, obj):
        return obj.remaining_quantity
    remaining_display.short_description = 'Còn lại'
    
    def status_display(self, obj):
        is_valid, message = obj.is_valid()
        if is_valid:
            return "✅ Hoạt động"
        return f"❌ {message}"
    status_display.short_description = 'Trạng thái'


@admin.register(VoucherUsage)
class VoucherUsageAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'user', 'order', 'discount_amount', 'order_total', 'used_at']
    list_filter = ['used_at', 'voucher']
    search_fields = ['user__email', 'voucher__code']
    readonly_fields = ['voucher', 'user', 'order', 'discount_amount', 'order_total', 'used_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ['user', 'voucher', 'collected_at', 'is_used']
    list_filter = ['is_used', 'collected_at']
    search_fields = ['user__email', 'voucher__code']
    readonly_fields = ['collected_at']
