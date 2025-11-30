from django.core.management.base import BaseCommand
from django.template import Template, Context
from django.core.mail import send_mail
from django.conf import settings

from mailings.models import Mailing, Attempt


class Command(BaseCommand):
    help = 'Отправить все рассылки со статусом "Создана"'

    def handle(self, *args, **options):
        mailings = Mailing.objects.filter(status='Создана')
        total = mailings.count()

        if total == 0:
            self.stdout.write(self.style.WARNING('Нет рассылок со статусом "Создана"'))
            return

        for mailing in mailings:
            success_count = 0
            for recipient in mailing.recipients.all():
                template = Template(mailing.message.body)
                body = template.render(Context({'name': recipient.full_name}))

                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    Attempt.objects.create(mailing=mailing, status='Успешно', server_response='250 OK')
                    success_count += 1
                except Exception as e:
                    Attempt.objects.create(mailing=mailing, status='Не успешно', server_response=str(e))

            mailing.status = 'Запущена'
            mailing.save()

            self.stdout.write(
                self.style.SUCCESS(f'{mailing} — отправлено {success_count} писем')
            )

        self.stdout.write(self.style.SUCCESS(f'Готово! Обработано {total} рассылок.'))