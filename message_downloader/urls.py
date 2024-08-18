from django.contrib import admin
from django.urls import path, include

from message_downloader import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logoutview, name='logout'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls', namespace='users')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
]
