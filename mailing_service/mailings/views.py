from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Recipient


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        # Пользователь видит только своих получателей
        return Recipient.objects.filter(user=self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:receipt_list')

    def form_valid(self, form):
        # Автоматически подставляем текущего пользователя как владельца
        form.instance.user = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:receipt_list')

    def get_queryset(self):
        # Редактировать можно только своих получателей
        return Recipient.objects.filter(owner=self.request.user)

class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def get_queryset(self):
        # Удалять можно только своих получателей
        return Recipient.objects.filter(owner=self.request.user)