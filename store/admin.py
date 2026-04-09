from django.contrib import admin
from .models import Sneaker, Category, SubCategory, Size

admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Size)
admin.site.register(Sneaker)