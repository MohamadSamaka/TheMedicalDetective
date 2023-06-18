from django.contrib import admin
from .models import CustomUser, CustomUserManager
from django.apps import AppConfig
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.apps import apps
from django.contrib.auth import get_user_model

from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, path
# from core.authentication.src.views.login import MyLoginView
from core.core.admin import BaseAdminSite


class MyAdminSite(BaseAdminSite):
    site_header = 'Admin Dashboard'
    site_title = 'Admin Dashboard'
    index_title = 'Admin Dashboard'
    # logout_template = 'client/pages/home.html'
    def get_urls(self):
        urls = super().get_urls()

        # Remove the change password URL
        # urls = [url for url in urls if not url.name == 'logout']
    
        custom_urls = [
            path('train-NER/', self.admin_view(self.NER_trainer), name='train_ner_model'),
            path('train-diagnoser/', self.admin_view(self.diagnose_trainer), name='train_diagnoser_model'),
        ]

        return custom_urls + urls

    
        
    def NER_trainer(self, request):
        from core.model_managment.src.models.NER import NERModel
        trainer = NERModel.Trainer()
        trainer.train_model()
        trainer.save_model()
        trainer.save_tokenizer()
        return HttpResponse("Training Done")
    
    def diagnose_trainer(self, request):
        from core.model_managment.src.models.diagnoser import DiagnoserModel
        trainer = DiagnoserModel.Trainer()
        trainer.train_model()
        trainer.save_model()
        return HttpResponse("Training Done")


# Create an instance of the custom AdminSite class
my_admin_site = MyAdminSite(name='adminpage-admin')


default_apps = ['auth', 'contenttypes', 'sessions', 'admin', 'messages', 'staticfiles']

# Get a list of all installed models
all_models = apps.get_models()

# Iterate over the models and register them if they belong to the default apps
for model in all_models:
    if model._meta.app_label in default_apps and not my_admin_site.is_registered(model):
        my_admin_site.register(model)

my_admin_site.register(CustomUser)

