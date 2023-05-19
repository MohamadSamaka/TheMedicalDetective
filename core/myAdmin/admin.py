from django.contrib import admin
from ..core.models import CustomUser
from .views import my_admin_site
from django.apps import AppConfig
from django.contrib.auth.models import Group



# class MyAppConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'Healthcare'

#     def ready(self):
#         # Define your custom group
#         group_name = 'My Custom Group'
#         group, created = Group.objects.get_or_create(name=group_name)

#         # Add permissions to the group
#         model_permissions = Permission.objects.filter(content_type__app_label='myapp', content_type__model='mymodel')
#         for permission in model_permissions:
#             if permission.codename.startswith('add') or permission.codename.startswith('change'):
#                 group.permissions.add(permission)

#         # Register your custom group
#         self.register_group(my_admin_site, group)

my_admin_site.register(Group)


my_admin_site.register(CustomUser)

