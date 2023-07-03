from .models import CustomUser
from django.apps import apps

from django.urls import re_path
from core.core.admin import BaseAdminSite
from django.http import Http404, FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import os
from django.contrib.admin import AdminSite


class MyAdminSite(BaseAdminSite):
    site_header = 'Admin Dashboard'
    site_title = 'Admin Dashboard'
    index_title = 'Admin Dashboard'
    site_name = 'admin-site'  # Unique namespace for the admin site
    
    def get_urls(self):
        # from core.chatbot_models_manager.admin import DiagnoserAdmin
        urls = super().get_urls()

        custom_urls = [
            re_path(r"^media/protected/(?P<file_path>.+)/$", self.admin_view(self.protected_files_provider), name="protected-media"),
        ]
        return custom_urls + urls
    
    def protected_files_provider(self, request, file_path):
        from pathlib import Path
        absolute_path = Path.joinpath(settings.PROTECTED_MEDIA_ABSOLUTE_URL, file_path)
        print('absolute path is: ', absolute_path)
        # Check if the file exists
        if os.path.exists(absolute_path):
            # Open the file and create a FileResponse
            file = open(absolute_path, 'rb')
            response = FileResponse(file)

            # Set the appropriate content type
            file_extension = os.path.splitext(file_path)[1]
            content_type = f'application/{file_extension}'
            response['Content-Type'] = content_type
            return response
        raise Http404('File not found.')

    

# Create an instance of the custom AdminSite class

my_user_site = MyAdminSite(name='user-page')

my_admin_site = MyAdminSite(name='adminpage-admin')


default_apps = ['auth', 'contenttypes', 'sessions', 'admin', 'messages', 'staticfiles']

# Get a list of all installed models
all_models = apps.get_models()

# Iterate over the models and register them if they belong to the default apps
for model in all_models:
    if model._meta.app_label in default_apps and not my_admin_site.is_registered(model):
        my_admin_site.register(model)

my_admin_site.register(CustomUser)
# my_user_site.register(CustomUser)
