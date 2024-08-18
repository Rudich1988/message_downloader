from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from apps.users.models import CustomUser
from apps.users.forms import UserRegistrationForm


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = CustomUser
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('login')
    success_message = 'Пользователь успешно зарегистрирован'
