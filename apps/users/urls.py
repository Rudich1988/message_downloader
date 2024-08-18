from django.urls import path

from .views import UserRegistrationView


app_name = 'users'

urlpatterns = [
    path('create/', UserRegistrationView.as_view(), name='create_user'),
]
