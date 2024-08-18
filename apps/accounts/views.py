from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic.list import ListView

from apps.accounts.models import UserEmailAccount
from apps.accounts.forms import AccountCreateForm


class AccountCreateView(SuccessMessageMixin, CreateView):
    model = UserEmailAccount
    form_class = AccountCreateForm
    template_name = 'accounts/create_account.html'
    success_url = reverse_lazy('index')
    success_message = 'Почта успешно добавлена'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AccountsShowView(ListView):
    model = UserEmailAccount
    template_name = 'accounts/show_accounts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = UserEmailAccount.objects.all()
        return context

