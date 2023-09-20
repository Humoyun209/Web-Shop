from django.db import models
from django.core.validators import MaxValueValidator


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from =models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    active = models.BooleanField()
    
    def __str__(self) -> str:
        return f'Coupon - "{self.code}"'