from django.db import models
from accounts.models import Account
from store.models import Product


class WishlistItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=200, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.product.product_name}"
        return f"Anonymous ({self.session_key[:8]}) - {self.product.product_name}"
