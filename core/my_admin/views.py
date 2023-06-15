from django.shortcuts import render
from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, path
from core.authentication.src.views.login import MyLoginView


class MyAdminSite(AdminSite):
    site_header = 'Dashboard'
    site_title = 'Dashboard'
    index_title = 'Dashboard'
    login_template = 'authentication/pages/log-in.html'
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

    def index(self, request, extra_context=None):
        # Your custom index view logic here
        extra_context = None
        print("*******My Admin Site Index*******")
        # if request.user.is_authenticated:
        
        return super().index(request, extra_context)

        
    
    def login(self, request, extra_context=None):
        print("My Admin Site login")
        if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
            # User is already logged in, redirect them to the admin index page
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            # User is not logged in, redirect them to your custom login page
            return MyLoginView.as_view()(request)
        
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
my_admin_site = MyAdminSite(name='myadmin')
