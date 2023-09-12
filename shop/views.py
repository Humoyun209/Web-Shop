from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from cart.forms import CartAddProductForm

from shop.models import Category, Product


def product_list(request: HttpRequest, category_slug=None) -> HttpResponse:
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = get_list_or_404(Product, category=category)

    return render(
        request,
        "shop/product/list.html",
        context={
            "category": category,
            "categories": categories,
            "products": products,
        },
    )


def product_detail(request: HttpRequest, id: int, slug: str) -> HttpResponse:
    product = get_object_or_404(Product, 
                                id=id,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    return render(request,
                  "shop/product/detail.html",
                  context={"product": product, 
                           'cart_product_form': cart_product_form})
