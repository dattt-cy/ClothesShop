from django.contrib import admin
from .models import WishlistItem


class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'session_key', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__product_name', 'user__email', 'session_key']
    readonly_fields = ['created_at']
    

admin.site.register(WishlistItem, WishlistItemAdmin)
