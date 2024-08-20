from django.urls import path
from apps.mail_messages.consumers import EmailMessageConsumer

ws_urlpatterns = [
    path('ws/email_messages/<int:email_account_id>/', EmailMessageConsumer.as_asgi())
]
