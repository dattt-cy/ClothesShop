"""
Script thêm màu sắc cho các sản phẩm
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beeshop.settings')
django.setup()

from store.models import Product, Variation

# Định nghĩa màu sắc cho từng loại sản phẩm
color_mappings = {
    # Jackets
    'jacket-boy1.png': ['Black', 'Navy Blue', 'Gray'],
    'jacket-boy2.png': ['Red', 'Blue', 'Black'],
    'jacket-boy3.png': ['Brown', 'Green', 'Black'],
    'jacket-boy4.png': ['Navy Blue', 'Gray', 'Olive'],
    'jacket-girl1.png': ['Pink', 'Purple', 'White'],
    'jacket-girl2.png': ['Beige', 'Light Pink', 'Cream'],
    'jacket-girl3.png': ['Red', 'Blue', 'Pink'],
    
    # Jeans
    'Jean.png': ['Dark Blue', 'Light Blue', 'Black'],
    'Jean-Girl.png': ['Blue', 'Light Blue', 'White'],
    
    # Shirts
    'shirt-boy1.png': ['White', 'Blue', 'Black'],
    'shirt-girl1.png': ['White', 'Pink', 'Lavender'],
    'shirt-girl2.png': ['Beige', 'Light Pink', 'White'],
    
    # T-Shirts
    'T-shirtboy1.png': ['Black', 'White', 'Gray'],
    'T-shirtboy2.png': ['Blue', 'Red', 'Green'],
    'T-shirtsboy3.png': ['Navy Blue', 'Black', 'Gray'],
    'T-shirtgirl1.png': ['Pink', 'White', 'Purple'],
    'T-shirtgirl2.png': ['Light Pink', 'Peach', 'White'],
    'T-shirtgirl3.png': ['Yellow', 'Pink', 'Blue'],
    'T-Shirt.png': ['Black', 'White', 'Gray', 'Navy Blue'],
    
    # Shoes
    'shoes-boy1.png': ['Black', 'White', 'Blue'],
    'shoes-boy2.png': ['Gray', 'Black', 'Navy Blue'],
    'shoes-boy3.png': ['Red', 'Black', 'White'],
    'shoes-girl1.png': ['Pink', 'White', 'Purple'],
    'shoes-girl2.png': ['Beige', 'White', 'Light Pink'],
    'shoes-girl3.png': ['Blue', 'Pink', 'White'],
}

print("=" * 70)
print("THÊM MÀU SẮC CHO SẢN PHẨM")
print("=" * 70)

added_count = 0
skipped_count = 0

for image_name, colors in color_mappings.items():
    try:
        # Tìm sản phẩm theo tên ảnh
        products = Product.objects.filter(images__contains=image_name)
        
        if not products.exists():
            print(f"⊘ {image_name}: Không tìm thấy sản phẩm")
            skipped_count += 1
            continue
        
        product = products.first()
        
        # Kiểm tra xem đã có color variations chưa
        existing_colors = Variation.objects.filter(
            product=product,
            variation_category='color'
        ).count()
        
        if existing_colors > 0:
            print(f"⊘ {product.product_name}: Đã có {existing_colors} màu")
            skipped_count += 1
            continue
        
        # Thêm màu sắc
        colors_added = 0
        for color in colors:
            Variation.objects.create(
                product=product,
                variation_category='color',
                variation_value=color,
                is_active=True
            )
            colors_added += 1
        
        print(f"✓ {product.product_name}: Đã thêm {colors_added} màu ({', '.join(colors)})")
        added_count += 1
        
    except Exception as e:
        print(f"✗ {image_name}: Lỗi - {str(e)}")

print("\n" + "=" * 70)
print("KẾT QUẢ")
print("=" * 70)
print(f"✓ Đã thêm màu cho: {added_count} sản phẩm")
print(f"⊘ Đã bỏ qua: {skipped_count} sản phẩm")
print("=" * 70)
