import stripe
from stripe.stripe_object import StripeObject
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from payment.tasks import invoice_to_email


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event: None | StripeObject = None
    
    try:
        event = stripe.Webhook.construct_event(payload=payload,
                                               sig_header=sig_header,
                                               secret=settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            order.stripe_id = session.payment_intent
            order.paid = True
            order.save()
            invoice_to_email.delay(order.id)
    
    return HttpResponse(status=200)