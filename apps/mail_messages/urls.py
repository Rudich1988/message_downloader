from django.urls import path

from .views import SaveEmail


app_name = 'mail_messages'

urlpatterns = [
    path('save_messages/<int:email_account_id>/', SaveEmail.as_view(), name='save_messages'),
]
