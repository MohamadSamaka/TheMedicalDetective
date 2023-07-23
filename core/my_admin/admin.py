from django.apps import apps
from django.urls import re_path
from django.http import Http404, FileResponse
from django.conf import settings
from .models import CustomUser
from core.core.admin import BaseAdminSite
from core.booking.models import Booking
from django.contrib.admin import ModelAdmin
from .src.admin_sites.user import UserAdminSite

class BookingAdmin(ModelAdmin):
    list_display = ('doctor', 'appointment_date_time')
    def get_queryset(self, request):
        return Booking.objects.filter(subject=request.user)


class MyAdminSite(BaseAdminSite):
    site_header = 'Admin Dashboard'
    site_title = 'Admin Dashboard'
    index_title = 'Admin Dashboard'
    site_name = 'admin-site'  # Unique namespace for the admin site
    
    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            re_path(r"^media/protected/(?P<file_path>.+)/$", self.admin_view(self.protected_files_provider), name="protected-media"),
        ]
        return custom_urls + urls
    
    def protected_files_provider(self, request, file_path):
        from pathlib import Path
        absolute_path = Path.joinpath(settings.PROTECTED_MEDIA_ABSOLUTE_URL, file_path)
        if absolute_path.exists():
            file_extension = absolute_path.suffix.lower()
            if file_extension != '.csv' and file_extension != '.json':
                raise ValueError(f"Unsupported file extension: {file_extension}")
            file = open(absolute_path, 'rb')
            response = FileResponse(file)
            content_type = f'application/{file_extension[1:]}'
            response['Content-Type'] = content_type
            # file.close()
            return response
        raise Http404('File not found.')


my_user_site = UserAdminSite(name='adminpage-user')


my_admin_site = MyAdminSite(name='adminpage-admin')


default_apps = ['auth', 'contenttypes', 'sessions', 'admin', 'messages', 'staticfiles']

# Get a list of all installed models
all_models = apps.get_models()

# Iterate over the models and register them if they belong to the default apps
for model in all_models:
    if model._meta.app_label in default_apps and not my_admin_site.is_registered(model):
        my_admin_site.register(model)

my_admin_site.register(CustomUser)
my_user_site.register(Booking, BookingAdmin)