import csv
import datetime

from django.urls import reverse

from orders.models import Order, OrderItem

from django.http import HttpRequest, HttpResponse
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.db.models.query import QuerySet


def order_stripe_payment(obj: Order):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ""


order_stripe_payment.short_description = "Stripe payment"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]


def export_to_csv(modeladmin: "OrderAdmin", request: HttpRequest, queryset: QuerySet):
    opts = modeladmin.model._meta
    content_disposition = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)
    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%Y-%m-%d")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = "Export to CSV"


def order_detail(obj):
    url = reverse("orders:admin_order_detail", args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_in_pdf(obj):
    url = reverse("orders:admin_order_pdf", args=[obj.id])
    return mark_safe(f'<a href="{url}">Invoice</a>')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        order_stripe_payment,
        "created",
        "updated",
        order_detail,
        order_in_pdf,
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    actions = [export_to_csv]
