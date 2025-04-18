from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.CharField(max_length=10, primary_key=True)  # e.g., P1009
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name