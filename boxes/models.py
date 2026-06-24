from django.db import models


class Box(models.Model):
    name = models.CharField(max_length=100)

    # DecimalField for dimensions — consistent with Product model
    # avoids mixed Decimal/float arithmetic errors in packing engine
    length = models.DecimalField(max_digits=7, decimal_places=2)
    width = models.DecimalField(max_digits=7, decimal_places=2)
    height = models.DecimalField(max_digits=7, decimal_places=2)

    max_weight = models.DecimalField(max_digits=8, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def volume(self):
        return self.length * self.width * self.height
