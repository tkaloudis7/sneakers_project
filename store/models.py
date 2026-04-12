from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories", verbose_name="Parent Category")
    name = models.CharField(max_length=100, verbose_name="Sub-Category Name")

    class Meta:
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

class Size(models.Model):
    name = models.CharField(max_length=10, verbose_name="Size")

    def __str__(self):
        return self.name

class Sneaker(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Sub-Category")
    name = models.CharField(max_length=150, verbose_name="Model Name")
    brand = models.CharField(max_length=50, verbose_name="Brand")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Price")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    image = models.ImageField(upload_to='sneakers_img/', blank=True, null=True, verbose_name="Image")
    sizes = models.ManyToManyField(Size, blank=True, verbose_name="Available Sizes")

    def __str__(self):
        return f"{self.brand} - {self.name}"


class Review(models.Model):
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField(default=5) # 1-5 star reviews
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.sneaker.name}"