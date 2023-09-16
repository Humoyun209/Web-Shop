from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from cart.cart import Cart

from orders.forms import OrderCreateForm
from orders.models import OrderItem
from orders.tasks import send_message_about_order_created


def order_create(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    cart: Cart = Cart(request)
    if request.method == 'POST':
        form: OrderCreateForm = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    price=item['price'],
                    quantity=item['quantity'],
                    product=item['product']
                )
            cart.clear()
            send_message_about_order_created.delay(order.id)
            request.session['order_id'] = order.id
            return redirect(reverse('payment:process'))
        return render(request,
                      'orders/order/created.html',
                      {'order': order})
    else:
        form: OrderCreateForm = OrderCreateForm()
        return render(request,
                      'orders/order/create.html',
                      {'form': form})