from django.urls import path

from .views import (AccountCreateView, AccountsShowView,
                    AccountDeleteView, AccountUpdateView)


app_name = 'accounts'

urlpatterns = [
    path('create/',
         AccountCreateView.as_view(),
         name='create_account'
         ),
    path('show_accounts/',
         AccountsShowView.as_view(),
         name='show_accounts'
         ),
    path('delete_account/<int:pk>',
         AccountDeleteView.as_view(),
         name='delete_account'),
    path('update_account/<int:pk>',
         AccountUpdateView.as_view(),
         name='update_account')
]
