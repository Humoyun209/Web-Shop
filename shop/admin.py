from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from .models import Category, Product
from parler.admin import TranslatableAdmin


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ['name', 'slug']

    def get_prepopulated_fields(self, request: HttpRequest, obj: Any | None = None) -> dict[str, tuple[str]]:
        return {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ['name', 'slug', 'price',
    'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
    
    def get_prepopulated_fields(self, request: HttpRequest, obj: Any | None = None) -> dict[str, tuple[str]]:
        return {'slug': ('name',)}
