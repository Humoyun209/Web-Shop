from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from cart.forms import CartAddProductForm

from shop.models import Category, Product
from shop.recommender import Recommender


def product_list(request: HttpRequest, category_slug=None) -> HttpResponse:
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()
    language = request.LANGUAGE_CODE

    if category_slug:
        category = get_object_or_404(Category, 
                                     translations__slug=category_slug,
                                     translations__language_code=language)
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
    language = request.LANGUAGE_CODE
    product = get_object_or_404(Product, 
                                id=id,
                                translations__slug=slug,
                                translations__language_code=language,
                                available=True)
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    cart_product_form = CartAddProductForm()
    return render(request,
                  "shop/product/detail.html",
                  context={"product": product, 
                           'cart_product_form': cart_product_form,
                           'recommended_products': recommended_products})
