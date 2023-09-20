from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.template.loader import render_to_string
import weasyprint

from cart.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem
from orders.tasks import send_message_about_order_created


def order_create(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    cart: Cart = Cart(request)
    if request.method == "POST":
        form: OrderCreateForm = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    price=item["price"],
                    quantity=item["quantity"],
                    product=item["product"],
                )
            cart.clear()
            send_message_about_order_created.delay(order.id)
            request.session["order_id"] = order.id
            return redirect(reverse("payment:process"))
        return render(request, "orders/order/created.html", {"order": order})
    else:
        form: OrderCreateForm = OrderCreateForm()
        return render(request, "orders/order/create.html", {"form": form})


@staff_member_required
def admin_order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "orders/admin/order/detail.html", {"order": order})


@staff_member_required
def generate_pdf_for_order(request: HttpRequest, order_id: int):
    order = get_object_or_404(Order, pk=order_id)
    html = render_to_string("orders/order/pdf.html", {"order": order})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename=order_{order_id}.pdf"
    weasyprint.HTML(string=html).write_pdf(
        response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / "css/pdf.css")]
    )
    return response
