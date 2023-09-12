from decimal import Decimal
from django.http import HttpRequest

from myshop import settings
from shop.models import Product


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if cart is None:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(
        self, product: Product, quantity: int = 1, override_quantity: bool = False
    ) -> None:
        product_id = str(product.pk)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def remove(self, product: Product) -> None:
        product_id = str(product.pk)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(pk__in=product_ids)
        for product in products:
            self.cart[str(product.pk)]["product"] = product
        cart = self.cart.copy()
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self) -> int:
        return sum([item["quantity"] for item in self.cart.values()])

    def get_total_price(self):
        return sum([item["quantity"] * Decimal(item["price"]) for item in self.cart.values()])

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self) -> None:
        self.session.modified = True
