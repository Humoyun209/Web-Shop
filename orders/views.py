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
from shop.models import Product
from shop.recommender import Recommender


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                        product=item['product'],
                                        price=item['price'],
                                        quantity=item['quantity'])
            # clear the cart
            cart.clear()
            # launch asynchronous task
            send_message_about_order_created.delay(order.id)
            # set the order in the session
            request.session['order_id'] = order.id
            # redirect for payment
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


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
