from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from cart.cart import Cart
from cart.forms import CartAddProductForm
from shop.models import Product


@require_POST
def cart_add(request: HttpRequest, product_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cart.add(
            product=product,
            quantity=form.cleaned_data["quantity"],
            override_quantity=form.cleaned_data["override"],
        )
    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request: HttpRequest, product_id: int):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id)
    cart.remove(product=product)
    return redirect("cart:cart_detail")


def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    return render(request, "cart/detail.html", {"cart": cart})
