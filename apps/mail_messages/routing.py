from django.urls import path
from apps.mail_messages.views import EmailConsumer

ws_urlpatterns = [
    path('ws/mail_messages/', EmailConsumer.as_asgi())
]
