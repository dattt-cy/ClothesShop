"""
Script tự động thêm sản phẩm từ ảnh trong thư mục media/photos/products
"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beeshop.settings')
django.setup()

from store.models import Product, Variation
from category.models import Category
from pathlib import Path

# Mapping tên file -> thông tin sản phẩm
products_data = [
    # Jackets - Boy
    {
        'name': 'Boys Casual Jacket 1',
        'image': 'jacket-boy1.png',
        'category': 'Jackets',
        'price': 85,
        'description': 'Stylish casual jacket for boys, perfect for everyday wear',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Boys Sports Jacket 2',
        'image': 'jacket-boy2.png',
        'category': 'Jackets',
        'price': 90,
        'description': 'Comfortable sports jacket for active boys',
        'variations': [
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
            {'type': 'size', 'value': 'XL'},
        ]
    },
    {
        'name': 'Boys Winter Jacket 3',
        'image': 'jacket-boy3.png',
        'category': 'Jackets',
        'price': 95,
        'description': 'Warm winter jacket for boys with modern design',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Boys Outdoor Jacket 4',
        'image': 'jacket-boy4.png',
        'category': 'Jackets',
        'price': 88,
        'description': 'Durable outdoor jacket for boys adventures',
        'variations': [
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
            {'type': 'size', 'value': 'XL'},
        ]
    },
    
    # Jackets - Girl
    {
        'name': 'Girls Fashion Jacket 1',
        'image': 'jacket-girl1.png',
        'category': 'Jackets',
        'price': 92,
        'description': 'Trendy fashion jacket for girls with elegant design',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Girls Casual Jacket 2',
        'image': 'jacket-girl2.png',
        'category': 'Jackets',
        'price': 87,
        'description': 'Comfortable casual jacket perfect for girls',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Girls Spring Jacket 3',
        'image': 'jacket-girl3.png',
        'category': 'Jackets',
        'price': 89,
        'description': 'Light spring jacket for girls with beautiful colors',
        'variations': [
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
            {'type': 'size', 'value': 'XL'},
        ]
    },
    
    # Jeans
    {
        'name': 'Boys Classic Jeans',
        'image': 'Jean.png',
        'category': 'Jeans',
        'price': 55,
        'description': 'Classic denim jeans for boys, comfortable fit',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
            {'type': 'size', 'value': 'XL'},
        ]
    },
    {
        'name': 'Girls Stylish Jeans',
        'image': 'Jean-Girl.png',
        'category': 'Jeans',
        'price': 58,
        'description': 'Stylish jeans for girls with modern cut',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    
    # Shirts - Boy
    {
        'name': 'Boys Casual Shirt',
        'image': 'shirt-boy1.png',
        'category': 'Shirts',
        'price': 35,
        'description': 'Comfortable casual shirt for boys',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    
    # Shirts - Girl
    {
        'name': 'Girls Elegant Shirt 1',
        'image': 'shirt-girl1.png',
        'category': 'Shirts',
        'price': 38,
        'description': 'Elegant shirt for girls with beautiful design',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Girls Fashion Shirt 2',
        'image': 'shirt-girl2.png',
        'category': 'Shirts',
        'price': 40,
        'description': 'Fashionable shirt for girls, perfect for any occasion',
        'variations': [
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
            {'type': 'size', 'value': 'XL'},
        ]
    },
    
    # T-Shirts - Boy
    {
        'name': 'Boys Cool T-Shirt 1',
        'image': 'T-shirtboy1.png',
        'category': 'T-Shirts',
        'price': 25,
        'description': 'Cool and comfortable t-shirt for boys',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Boys Graphic T-Shirt 2',
        'image': 'T-shirtboy2.png',
        'category': 'T-Shirts',
        'price': 28,
        'description': 'Trendy graphic t-shirt for boys',
        'variations': [
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
            {'type': 'size', 'value': 'XL'},
        ]
    },
    {
        'name': 'Boys Sports T-Shirt 3',
        'image': 'T-shirtsboy3.png',
        'category': 'T-Shirts',
        'price': 27,
        'description': 'Athletic sports t-shirt for active boys',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    
    # T-Shirts - Girl
    {
        'name': 'Girls Cute T-Shirt 1',
        'image': 'T-shirtgirl1.png',
        'category': 'T-Shirts',
        'price': 26,
        'description': 'Cute and comfy t-shirt for girls',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Girls Fashion T-Shirt 2',
        'image': 'T-shirtgirl2.png',
        'category': 'T-Shirts',
        'price': 29,
        'description': 'Fashionable t-shirt for stylish girls',
        'variations': [
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Girls Summer T-Shirt 3',
        'image': 'T-shirtgirl3.png',
        'category': 'T-Shirts',
        'price': 27,
        'description': 'Light summer t-shirt for girls',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
        ]
    },
    {
        'name': 'Classic T-Shirt',
        'image': 'T-Shirt.png',
        'category': 'T-Shirts',
        'price': 24,
        'description': 'Classic unisex t-shirt for everyone',
        'variations': [
            {'type': 'size', 'value': 'S'},
            {'type': 'size', 'value': 'M'},
            {'type': 'size', 'value': 'L'},
            {'type': 'size', 'value': 'XL'},
        ]
    },
    
    # Shoes - Boy
    {
        'name': 'Boys Sport Shoes 1',
        'image': 'shoes-boy1.png',
        'category': 'Shoes',
        'price': 65,
        'description': 'Comfortable sport shoes for boys',
        'variations': [
            {'type': 'size', 'value': '38'},
            {'type': 'size', 'value': '39'},
            {'type': 'size', 'value': '40'},
            {'type': 'size', 'value': '41'},
        ]
    },
    {
        'name': 'Boys Casual Shoes 2',
        'image': 'shoes-boy2.png',
        'category': 'Shoes',
        'price': 68,
        'description': 'Stylish casual shoes for boys',
        'variations': [
            {'type': 'size', 'value': '39'},
            {'type': 'size', 'value': '40'},
            {'type': 'size', 'value': '41'},
            {'type': 'size', 'value': '42'},
        ]
    },
    {
        'name': 'Boys Running Shoes 3',
        'image': 'shoes-boy3.png',
        'category': 'Shoes',
        'price': 72,
        'description': 'High-performance running shoes for boys',
        'variations': [
            {'type': 'size', 'value': '38'},
            {'type': 'size', 'value': '39'},
            {'type': 'size', 'value': '40'},
        ]
    },
    
    # Shoes - Girl
    {
        'name': 'Girls Fashion Shoes 1',
        'image': 'shoes-girl1.png',
        'category': 'Shoes',
        'price': 70,
        'description': 'Fashionable shoes for girls',
        'variations': [
            {'type': 'size', 'value': '36'},
            {'type': 'size', 'value': '37'},
            {'type': 'size', 'value': '38'},
            {'type': 'size', 'value': '39'},
        ]
    },
    {
        'name': 'Girls Casual Shoes 2',
        'image': 'shoes-girl2.png',
        'category': 'Shoes',
        'price': 67,
        'description': 'Comfortable casual shoes for girls',
        'variations': [
            {'type': 'size', 'value': '36'},
            {'type': 'size', 'value': '37'},
            {'type': 'size', 'value': '38'},
        ]
    },
    {
        'name': 'Girls Sport Shoes 3',
        'image': 'shoes-girl3.png',
        'category': 'Shoes',
        'price': 69,
        'description': 'Athletic sport shoes for girls',
        'variations': [
            {'type': 'size', 'value': '37'},
            {'type': 'size', 'value': '38'},
            {'type': 'size', 'value': '39'},
        ]
    },
]

print("=" * 70)
print("THÊM SẢN PHẨM MỚI VÀO DATABASE")
print("=" * 70)

added_count = 0
skipped_count = 0
error_count = 0

for product_info in products_data:
    try:
        # Kiểm tra xem sản phẩm đã tồn tại chưa (dựa vào tên ảnh)
        if Product.objects.filter(images__contains=product_info['image']).exists():
            print(f"⊘ {product_info['name']}: Đã tồn tại")
            skipped_count += 1
            continue
        
        # Lấy category
        try:
            category = Category.objects.get(category_name=product_info['category'])
        except Category.DoesNotExist:
            print(f"✗ {product_info['name']}: Không tìm thấy category '{product_info['category']}'")
            error_count += 1
            continue
        
        # Tạo slug từ tên
        from django.utils.text import slugify
        slug = slugify(product_info['name'])
        
        # Đảm bảo slug unique
        original_slug = slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Tạo product
        product = Product.objects.create(
            product_name=product_info['name'],
            slug=slug,
            description=product_info['description'],
            price=product_info['price'],
            images=f"photos/products/{product_info['image']}",
            stock=random.randint(10, 50),  # Random stock từ 10-50
            is_available=True,
            category=category
        )
        
        # Tạo variations
        for var_info in product_info['variations']:
            Variation.objects.create(
                product=product,
                variation_category=var_info['type'],
                variation_value=var_info['value'],
                is_active=True
            )
        
        print(f"✓ {product_info['name']}: Đã thêm ({len(product_info['variations'])} variations)")
        added_count += 1
        
    except Exception as e:
        print(f"✗ {product_info['name']}: Lỗi - {str(e)}")
        error_count += 1

print("\n" + "=" * 70)
print("KẾT QUẢ")
print("=" * 70)
print(f"✓ Đã thêm: {added_count} sản phẩm")
print(f"⊘ Đã bỏ qua: {skipped_count} sản phẩm")
print(f"✗ Lỗi: {error_count} sản phẩm")
print("=" * 70)
