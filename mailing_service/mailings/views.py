from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.template import Template, Context
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Recipient, Message, Mailing, Attempt


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        # Пользователь видит только своих получателей
        return Recipient.objects.filter(owner=self.request.user)


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def form_valid(self, form):
        # Автоматически подставляем текущего пользователя как владельца
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    fields = ['email', 'full_name', 'comment']
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def get_queryset(self):
        # Редактировать можно только своих получателей
        return Recipient.objects.filter(owner=self.request.user)

class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def get_queryset(self):
        # Удалять можно только своих получателей
        def get_queryset(self):
            user = self.request.user
            if user.groups.filter(name='Менеджеры').exists():
                return Recipient.objects.all()  # Менеджер — видит ВСЕХ получателей
            return Recipient.objects.filter(owner=user)  # Обычный — только своих

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджеры').exists():
            return Message.objects.all()  # Менеджер — видит ВСЕ сообщения
        return Message.objects.filter(owner=user)  # Обычный — только свои


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['subject', 'body']
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Менеджеры').exists():
            return Mailing.objects.all()  # Менеджер — видит ВСЕ рассылки
        return Mailing.objects.filter(owner=user)  # Обычный — только свои


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ['status', 'start_time', 'end_time', 'message', 'recipients']
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ['status', 'start_time', 'end_time', 'message', 'recipients']
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

@login_required
def mailing_send(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    # Проверка статуса
    if mailing.status != 'Создана':
        # просто редирект
        return redirect('mailings:mailing_list')

    success_count = 0
    for recipient in mailing.recipients.all():
        # Рендерим тело письма
        template = Template(mailing.message.body)
        context = Context({'name': recipient.full_name})
        body = template.render(context)

        try:
            send_mail(
                subject=mailing.message.subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            Attempt.objects.create(
                mailing=mailing,
                status='Успешно',
                server_response='250 OK'
            )
            success_count += 1
        except Exception as e:
            Attempt.objects.create(
                mailing=mailing,
                status='Не успешно',
                server_response=str(e)
            )

    # Меняю статус после отправки
    mailing.status = 'Запущена'
    mailing.save()

    # Передадаю статистику в список
    return redirect('mailings:mailing_list')