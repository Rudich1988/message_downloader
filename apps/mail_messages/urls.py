from django.urls import path

from .views import ShowEmailMessages, MessageDetailView


app_name = 'mail_messages'

urlpatterns = [
    path('save_messages/<int:email_account_id>/',
         ShowEmailMessages.as_view(),
         name='show_email_messages'
         ),
    path('message_detail/<int:pk>/',
         MessageDetailView.as_view(),
         name='message_detail'),
]

