from decimal import Decimal
from django.db import models
from shop.models import Product


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f'Order #{self.pk}'
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, 
                              on_delete=models.CASCADE, 
                              related_name='items')
    product = models.ForeignKey(Product, null=True,
                                on_delete=models.SET_NULL,
                                related_name='order_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self) -> str:
        return f'Order-item #{self.id}'
    
    def get_cost(self) -> Decimal:
        return self.price * self.quantity
    