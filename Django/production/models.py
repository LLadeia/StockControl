from django.db import models
from simple_history.models import HistoricalRecords


def upload_to(instance, filename):
    return f'file_pessoa/{filename}'


class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    stock = models.FloatField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    history = HistoricalRecords()
    image = models.ImageField(upload_to='raw_materials/', null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    stock = models.FloatField(default=0)
    history = HistoricalRecords()
    image = models.ImageField(upload_to='products/', null=True, blank=True)

class ProductRawMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    manufacturing_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    quantity = models.FloatField()
    history = HistoricalRecords()

    @property
    def material_cost(self):
        try:
            return float(self.quantity) * float(self.raw_material.price or 0)
        except Exception:
            return 0

class ProductionLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.created_at}"

