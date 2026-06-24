from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)

    # DecimalField for dimensions and weight — avoids floating point rounding errors
    # that FloatField causes (e.g. 10.1 + 0.2 = 10.299999... in FloatField)
    # max_digits=7, decimal_places=2 supports up to 99999.99 cm — enough for any product
    length = models.DecimalField(max_digits=7, decimal_places=2)
    width  = models.DecimalField(max_digits=7, decimal_places=2)
    height = models.DecimalField(max_digits=7, decimal_places=2)

    # Weight in grams — DecimalField keeps precision for cost calculations downstream
    weight = models.DecimalField(max_digits=8, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.length}×{self.width}×{self.height} cm, {self.weight}g)"
