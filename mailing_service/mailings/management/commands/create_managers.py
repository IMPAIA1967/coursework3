from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailings.models import Recipient, Message, Mailing

class Command(BaseCommand):

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        recipient_ct = ContentType.objects.get_for_model(Recipient)
        message_ct = ContentType.objects.get_for_model(Message)
        mailing_ct = ContentType.objects.get_for_model(Mailing)

        perms = [
            Permission.objects.get(codename='view_all_recipients', content_type=recipient_ct),
            Permission.objects.get(codename='view_all_messages', content_type=message_ct),
            Permission.objects.get(codename='view_all_mailings', content_type=mailing_ct),
        ]

        group.permissions.set(perms)

        if created:
            self.stdout.write(self.style.SUCCESS('Группа «Менеджеры» создана и права назначены.'))
        else:
            self.stdout.write(self.style.WARNING('Группа «Менеджеры» уже существует. Права обновлены.'))