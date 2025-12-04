# 🎟️ HỆ THỐNG VOUCHER - HƯỚNG DẪN SỬ DỤNG

## ✅ ĐÃ HOÀN THÀNH

### 1. Models (3 bảng database)
- ✅ `Voucher` - Quản lý voucher
- ✅ `VoucherUsage` - Lịch sử sử dụng
- ✅ `UserVoucher` - Voucher đã thu thập

### 2. Admin Panel
- ✅ Quản lý voucher đầy đủ
- ✅ Hiển thị trạng thái, số lượng còn lại
- ✅ Lịch sử sử dụng (read-only)

### 3. Views & URLs
- ✅ Trang danh sách voucher
- ✅ Thu thập voucher
- ✅ Áp dụng voucher (AJAX)
- ✅ Xóa voucher (AJAX)

### 4. Templates
- ✅ Trang voucher list đẹp mắt
- ✅ Dark mode support
- ✅ Responsive design

### 5. Navigation
- ✅ Link "Vouchers" trong navbar

---

## 📝 HƯỚNG DẪN TẠO VOUCHER MẪU

### Bước 1: Vào Admin Panel
```
http://127.0.0.1:8000/admin/
```

### Bước 2: Tạo Voucher
Vào **Vouchers → Vouchers → Add Voucher**

#### VÍ DỤ 1: Giảm 20% (tối đa 100k)
```
Code: NEWUSER2025
Description: Giảm 20% cho khách hàng mới
Discount type: Percentage
Discount value: 20
Min purchase: 200000
Max discount: 100000
Total quantity: 100 (hoặc 0 = không giới hạn)
Per user limit: 1
Start date: 04/12/2025 00:00
End date: 31/12/2025 23:59
Is active: ✅
```

#### VÍ DỤ 2: Giảm cố định 50k
```
Code: FLASHSALE50
Description: Flash Sale - Giảm 50k cho đơn từ 300k
Discount type: Fixed Amount
Discount value: 50000
Min purchase: 300000
Max discount: (để trống)
Total quantity: 50
Per user limit: 2
Start date: 04/12/2025 00:00
End date: 10/12/2025 23:59
Is active: ✅
```

#### VÍ DỤ 3: Miễn phí ship
```
Code: FREESHIP
Description: Miễn phí vận chuyển toàn quốc
Discount type: Free Shipping
Discount value: 0
Min purchase: 500000
Max discount: (để trống)
Total quantity: 0 (không giới hạn)
Per user limit: 0 (không giới hạn)
Start date: 04/12/2025 00:00
End date: 31/12/2025 23:59
Is active: ✅
```

---

## 🚀 CÁCH SỬ DỤNG

### 1. Xem voucher
```
http://127.0.0.1:8000/vouchers/
```

### 2. Thu thập voucher
- Click "Collect Voucher" trên voucher bất kỳ
- Voucher sẽ vào "My Vouchers"

### 3. Sử dụng voucher (TIẾP THEO)
**CHƯA LÀM:**
- Tích hợp vào trang Cart
- Tích hợp vào trang Checkout
- Lưu voucher khi đặt hàng

---

## 📋 VIỆC CẦN LÀM TIẾP

### Phase 2: Tích hợp vào Cart/Checkout (30-45 phút)

1. **Thêm ô nhập voucher vào cart.html**
```html
<!-- Thêm vào templates/store/cart.html -->
<div class="voucher-section">
    <input type="text" id="voucher_code" placeholder="Nhập mã voucher">
    <button onclick="applyVoucher()">Áp dụng</button>
</div>
```

2. **AJAX apply voucher**
```javascript
function applyVoucher() {
    const code = document.getElementById('voucher_code').value;
    // Gọi API /vouchers/apply/
    // Cập nhật tổng tiền
}
```

3. **Cập nhật Order model**
```python
# Thêm vào orders/models.py
class Order:
    voucher = models.ForeignKey(Voucher, null=True, blank=True)
    voucher_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
```

4. **Lưu voucher khi place_order**
```python
# Trong orders/views.py
if request.session.get('voucher_code'):
    voucher = Voucher.objects.get(code=request.session['voucher_code'])
    order.voucher = voucher
    order.voucher_discount = voucher.calculate_discount(total)
    
    # Tạo VoucherUsage
    VoucherUsage.objects.create(
        voucher=voucher,
        user=request.user,
        order=order,
        discount_amount=order.voucher_discount
    )
    
    # Tăng used_quantity
    voucher.used_quantity += 1
    voucher.save()
```

---

## 🎨 TÍNH NĂNG NÂNG CAO (Optional)

### 1. Auto-apply best voucher
- Tự động chọn voucher tốt nhất cho user

### 2. Email Marketing
- Gửi voucher qua email vào dịp đặc biệt

### 3. Lucky Wheel
- Quay số trúng voucher

### 4. Gift Voucher
- Tặng voucher cho bạn bè

### 5. Countdown Timer
- Hiển thị thời gian còn lại của voucher

---

## 📊 DATABASE SCHEMA

```
Voucher
├── id (PK)
├── code (unique)
├── description
├── discount_type (percentage/fixed/freeship)
├── discount_value
├── min_purchase
├── max_discount
├── total_quantity
├── used_quantity
├── per_user_limit
├── start_date
├── end_date
├── is_active
├── created_at
└── updated_at

VoucherUsage
├── id (PK)
├── voucher_id (FK)
├── user_id (FK)
├── order_id (FK)
├── discount_amount
├── order_total
└── used_at

UserVoucher
├── id (PK)
├── user_id (FK)
├── voucher_id (FK)
├── collected_at
└── is_used
```

---

## 🔧 TROUBLESHOOTING

### Lỗi: "Voucher không tồn tại"
- Kiểm tra code nhập đúng chưa (phân biệt hoa/thường)
- Kiểm tra voucher is_active = True

### Lỗi: "Voucher đã hết hạn"
- Kiểm tra start_date và end_date
- Đảm bảo hiện tại nằm trong khoảng thời gian

### Lỗi: "Đơn hàng tối thiểu..."
- Kiểm tra min_purchase của voucher
- Đảm bảo giỏ hàng đủ điều kiện

---

## ✨ DEMO

1. Khởi động server:
```bash
.\env311\Scripts\Activate.ps1
python manage.py runserver
```

2. Tạo voucher mẫu trong admin

3. Truy cập: http://127.0.0.1:8000/vouchers/

4. Thu thập voucher và test!

---

**Bạn muốn tôi làm Phase 2 (tích hợp vào Cart/Checkout) ngay không?** 🚀
