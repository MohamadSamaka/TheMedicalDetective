from django.contrib import admin
from .models import CustomUser, CustomUserManager
from django.apps import AppConfig
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.apps import apps
from django.contrib.auth import get_user_model

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, path, re_path
# from core.authentication.src.views.login import MyLoginView
from core.core.admin import BaseAdminSite
from django.http import Http404, FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin import AdminSite



# def func():
#     import time
#     progress = 0
#     for i in range(10):
#         progress += 10
#         # Send progress update to all connected consumers
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             "train",
#             {
#                 'type': 'send_progress_update',
#                 'progress': progress,
#             }
#         )
#         time.sleep(1)  # Wait for 1 second before sending the next progress update

# class MyAdminSite(AdminSite):
#     site_header = 'User Dashboard'
#     site_title = 'User Dashboard'
#     index_title = 'User Dashboard'
    



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
            path('train-NER/', self.admin_view(self.NER_trainer), name='train_ner_model'),
            # path('train-diagnoser/', self.diagnose_trainer, name='das'),
        ]
        return custom_urls + urls
    
    # def custom_add_view(self, request):
    #     from django.template.response import TemplateResponse
    #     from django.template.loader import render_to_string
    #     from django.http import JsonResponse
    #     if request.method == 'POST':
    #         # Perform form submission
    #         form = self.get_form(request)
    #         if form.is_valid():
    #             # Process the form data (e.g., save to database)
    #             form.save()
    #             return JsonResponse({'success': True})
    #         else:
    #             # Return the form errors
    #             error_html = render_to_string('admin/diagnoser/diagnoser_add.html', {'errors': form.errors})
    #             return JsonResponse({'success': False, 'error_html': error_html})
    #     else:
    #         # Render the custom add form
    #         context = self.admin_site.each_context(request)
    #         return TemplateResponse(request, self.change_form_template, context)
    
    # @staff_member_required
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

    
        
    def NER_trainer(self, request):
        from core.chatbot_models_manager.src.models.NER import NERModel
        trainer = NERModel.Trainer()
        trainer.train_model()
        trainer.save_model()
        trainer.save_tokenizer()
        return HttpResponse("Training Done")
    
    # def diagnose_trainer(self, request):
    #     import tempfile
    #     import threading
    #     from core.chatbot_models_manager.src.models.diagnoser import DiagnoserModel
    #     trainer = DiagnoserModel.Trainer(dense1_n_neurons=64, dense2_n_neurons = 32, iterations=5)
    #     trainer.train_model()
    #     return HttpResponse("Training Done")
    
    # @method_decorator(csrf_exempt)  # Apply the csrf_exempt decorator
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    
    # async def test(self, request):
    #     from channels.layers import get_channel_layer
    #     progress = 0
    #     for i in range(10):
    #         progress += 10

    #         # Send progress update to all connected consumers
    #         channel_layer = get_channel_layer()
    #         await channel_layer.group_send(
    #             "train",
    #             {
    #                 'type': 'send_progress_update',
    #                 'progress': progress,
    #             }
    #         )
    
    


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
