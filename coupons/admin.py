from django.contrib import admin

from coupons.models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'discount', 'active']
    list_filter = ['active', 'discount', 'valid_to', 'valid_from']
    search_fields = ['code']
    
