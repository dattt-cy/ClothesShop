from django.db import models

# Create your models here.
class Category(models.Models):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255)
    cat_image = models.ImageField(upload='photos/categories', blank=True)

    def __str__(self):
        return self.category_name
