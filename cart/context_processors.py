from django.http import HttpRequest

from cart.cart import Cart


def cart(request: HttpRequest) -> dict[str, Cart]:
    return {'cart': Cart(request)}