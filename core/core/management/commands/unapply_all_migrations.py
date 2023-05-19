from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Unapply all migrations for all installed apps'

    def handle(self, *args, **options):
        app_configs = apps.get_app_configs()
        for app_config in app_configs:
            app_label = app_config.label
            self.stdout.write(f'Unapplying migrations for app: {app_label}')
            try:
                call_command('migrate', app_label, 'zero')
            except:
                self.stdout.write(self.style.WARNING(f"App '{app_label}' does not have migrations."))
