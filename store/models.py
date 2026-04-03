from django.db import models
from django.contrib.auth.models import User


class Brand(models.Model):
    name = models.CharField(max_length=100)


    def __str__(self):
        return self.name

class Sneaker(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    size = models.IntegerField()
    image = models.ImageField(upload_to='sneakers/')

    def __str__(self):
        return f"{self.brand.name} {self.name}"

class Review(models.Model):
    sneaker = models.ForeignKey(Sneaker, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.user.username} for {self.sneaker.name}"
