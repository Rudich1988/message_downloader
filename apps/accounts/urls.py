from django.urls import path

from .views import AccountCreateView, AccountsShowView, AccountDetailView


app_name = 'accounts'

urlpatterns = [
    path('create/', AccountCreateView.as_view(), name='create_account'),
    path('show_accounts/', AccountsShowView.as_view(), name='show_accounts'),
    path('<int:pk>/', AccountDetailView.as_view(), name='show_messages1'),
]
