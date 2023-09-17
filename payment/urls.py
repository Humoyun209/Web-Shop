from django.urls import path

from payment import views, webhooks


app_name = 'payment'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('completed/', views.payment_completed, name='completed'),
    path('cancelled/', views.payment_canceled, name='cancelled'),
    path('webhook/', webhooks.stripe_webhook, name='stripe-webhook'),
]