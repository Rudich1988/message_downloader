from django.urls import path
from .views import EmailConsumer

ws_urlpatterns = [
    path('ws/mail_messages/', EmailConsumer.as_asgi())
]
