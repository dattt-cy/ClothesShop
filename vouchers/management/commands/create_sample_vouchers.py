from django.core.management.base import BaseCommand
from vouchers.models import Voucher
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Tạo dữ liệu voucher mẫu'

    def handle(self, *args, **kwargs):
        # Xóa voucher cũ (nếu có)
        Voucher.objects.all().delete()
        
        now = timezone.now()
        
        vouchers_data = [
            {
                'code': 'NEWUSER2025',
                'description': 'Voucher chào mừng thành viên mới - Giảm 20% cho đơn hàng đầu tiên',
                'discount_type': 'percentage',
                'discount_value': 20,
                'min_purchase': 50,
                'max_discount': 20,
                'total_quantity': 100,
                'per_user_limit': 1,
                'start_date': now,
                'end_date': now + timedelta(days=30),
                'is_active': True,
            },
            {
                'code': 'FLASHSALE50',
                'description': 'Flash Sale - Giảm ngay $10 cho đơn hàng từ $30',
                'discount_type': 'fixed',
                'discount_value': 10,
                'min_purchase': 30,
                'max_discount': None,
                'total_quantity': 200,
                'per_user_limit': 2,
                'start_date': now,
                'end_date': now + timedelta(days=7),
                'is_active': True,
            },
            {
                'code': 'FREESHIP',
                'description': 'Miễn phí vận chuyển toàn quốc - Không giới hạn số lượng',
                'discount_type': 'freeship',
                'discount_value': 0,
                'min_purchase': 100,
                'max_discount': None,
                'total_quantity': 0,  # Unlimited
                'per_user_limit': 0,  # Unlimited
                'start_date': now,
                'end_date': now + timedelta(days=60),
                'is_active': True,
            },
            {
                'code': 'MEGA100',
                'description': 'Siêu sale - Giảm $25 cho đơn hàng từ $200',
                'discount_type': 'fixed',
                'discount_value': 25,
                'min_purchase': 200,
                'max_discount': None,
                'total_quantity': 50,
                'per_user_limit': 1,
                'start_date': now,
                'end_date': now + timedelta(days=14),
                'is_active': True,
            },
            {
                'code': 'SAVE30',
                'description': 'Tiết kiệm 30% - Tối đa $50 cho đơn hàng từ $100',
                'discount_type': 'percentage',
                'discount_value': 30,
                'min_purchase': 100,
                'max_discount': 50,
                'total_quantity': 150,
                'per_user_limit': 3,
                'start_date': now,
                'end_date': now + timedelta(days=21),
                'is_active': True,
            },
            {
                'code': 'VIP50OFF',
                'description': 'VIP Members Only - Giảm 50% tối đa $100',
                'discount_type': 'percentage',
                'discount_value': 50,
                'min_purchase': 150,
                'max_discount': 100,
                'total_quantity': 30,
                'per_user_limit': 1,
                'start_date': now,
                'end_date': now + timedelta(days=45),
                'is_active': True,
            },
        ]
        
        created_count = 0
        for voucher_data in vouchers_data:
            voucher = Voucher.objects.create(**voucher_data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created voucher: {voucher.code} - {voucher.get_discount_display()}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully created {created_count} vouchers!')
        )
