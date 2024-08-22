from django.views.generic.edit import (CreateView,
                                       DeleteView,
                                       UpdateView)
from django.urls import reverse_lazy
from django.views.generic.list import ListView

from apps.accounts.models import UserEmailAccount
from apps.accounts.forms import AccountCreateForm


class AccountCreateView(CreateView):
    model = UserEmailAccount
    form_class = AccountCreateForm
    template_name = 'accounts/create_account.html'
    success_url = reverse_lazy('accounts:show_accounts')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AccountsShowView(ListView):
    model = UserEmailAccount
    template_name = 'accounts/show_accounts.html'

    def get_queryset(self):
        owner = UserEmailAccount.objects.filter(owner=self.request.user)
        return owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accounts'] = self.get_queryset()
        return context


class AccountDeleteView(DeleteView):
    template_name = 'accounts/delete_account.html'
    model = UserEmailAccount
    success_url = reverse_lazy('index')


class AccountUpdateView(UpdateView):
    template_name = 'accounts/update_account.html'
    model = UserEmailAccount
    form_class = AccountCreateForm
    success_url = reverse_lazy('accounts:show_accounts')
