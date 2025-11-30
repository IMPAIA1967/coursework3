from django.db import models
from userapp.models import User


class Recipient(models.Model):
    email = models.EmailField(unique=True)  # уникальный e-mail
    full_name = models.CharField(max_length=200)  # Ф.И.О.
    comment = models.TextField(blank=True, null=True)  # необязательный комментарий
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.email

    class Meta:
        permissions = [
            ("view_all_recipients", "Может просматривать всех получателей"),
        ]


class Message(models.Model):
    subject = models.CharField(max_length=200)  # тема письма
    body = models.TextField()  # тело письма
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject

    class Meta:
        permissions = [
            ("view_all_messages", "Может просматривать все сообщения"),
        ]


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField()  # Дата и время первой отправки
    end_time = models.DateTimeField()  # Дата и время окончания
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Создана')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # владелец рассылки

    def __str__(self):
        return f'Рассылка {self.id}'

    def total_attempts(self):
        return self.attempt_set.count()

    def successful_attempts(self):
        return self.attempt_set.filter(status='success').count()

    def failed_attempts(self):
        return self.attempt_set.filter(status='error').count()

    def messages_sent(self):
        return self.successful_attempts()

    class Meta:
        permissions = [
            ("view_all_mailings", "Может просматривать все рассылки"),
        ]


class Attempt(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    attempt_time = models.DateTimeField(auto_now_add=True)  # фиксируется автоматически
    status = models.CharField(
        max_length=12,
        choices=[
            ('success', 'Успешно'),
            ('error', 'Не успешно'),
        ]
    )
    server_response = models.TextField(blank=True, null=True)  # ответ сервера

    def __str__(self):
        return f'Попытка {self.id} ({self.get_status_display()})'
