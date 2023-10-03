from django import template
from shop.models import Product

from shop.recommender import Recommender

register = template.Library()


@register.inclusion_tag('shop/product/recommender.html')
def get_recommended_products(recommended_products):
    return {'recommended_products': recommended_products}
    