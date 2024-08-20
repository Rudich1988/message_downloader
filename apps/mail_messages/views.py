from django.views.generic.list import ListView

from .models import EmailMessage


class SaveEmail(ListView):
    model = EmailMessage
    template_name = 'messages/show_messages.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email_account_id = self.kwargs['email_account_id']
        context['email_account_id'] = email_account_id
        context['messages'] = EmailMessage.objects.filter(account__id=email_account_id).order_by('-received_date')
        return context
