from decimal import Decimal

from coupons.models import Coupon
from shop.models import Product

from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator




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
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(Coupon, 
                               on_delete=models.SET_NULL,
                               related_name='orders',
                               blank=True, null=True)
    discount = models.PositiveBigIntegerField(default=0,
                                              validators=[MaxValueValidator(100)])
    
    def __str__(self) -> str:
        return f'Order #{self.pk}'
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
    
    def get_total_cost_before_discount(self):
        return sum(item.price for item in self.items.all())
    
    def get_discount(self):
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)
    
    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()
    
    def get_stripe_url(self) -> str:
        if not self.stripe_id:
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            path =  '/test/'
        else:
            path = '/'
        return f'https://dashboard.stripe.com{path}payments/{self.stripe_id}'


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
    