from django.db import models


class Recipient(models.Model):
    email = models.EmailField(unique=True) # уникальный e-mail
    full_name = models.CharField(max_length=200) # Ф.И.О.
    comment = models.TextField(blank=True, null=True) # необязательный комментарий
    owner = models.ForeignKey('userapp.User', on_delete=models.CASCADE)


    def __str__(self):
        return self.email

class Message(models.Model):
    objects = None
    subject = models.CharField(max_length=200) # тема письма
    body = models.TextField() # тело письма
    owner = models.ForeignKey('userapp.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.subject

class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField() # Дата и время первой отправки
    end_time = models.DateTimeField() # Дата и время окончания
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='Создана')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)
    owner = models.ForeignKey('userapp.User', on_delete=models.CASCADE) # владелец рассылки


    def __str__(self):
        return f'Рассылка {self.id}'

class Attempt(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    attempt_time = models.DateTimeField(auto_now_add=True) # auto_now_add-автоматически фиксируем время попытки
    status = models.CharField(max_length=12,
                              choices=[('success', 'Успешно'), # в базу и админку
                                       ('error', 'Не успешно'),])
    server_response = models.TextField(blank=True, null=True) # ответ_сервера

    def __str__(self):
        return f'Попытка {self.id} ({self.status})'
