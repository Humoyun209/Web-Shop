from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order


@shared_task
def invoice_to_email(order_id: int) -> None:
    order = Order.objects.get(id=order_id)
    subject = f'My Shop – Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject, message, 'test@mail.ru', [order.email])
    
    html: str = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    
    email.attach(f'order_{order_id}.pdf',
                 out.getvalue(),
                 'application/pdf')
    email.send()
    
    