from django.shortcuts import render
from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from core.authentication.src.views.login import MyLoginView


class MyAdminSite(AdminSite):
    site_header = 'Dashboard'
    site_title = 'Dashboard'
    index_title = 'Dashboard'
    login_template = 'authentication/pages/log-in.html'
    # logout_template = 'client/pages/home.html'
    # def get_urls(self):
    #     urls = super().get_urls()
    #     # Remove the change password URL
    #     # urls = [url for url in urls if not url.name == 'logout']
        
    #     # # Remove the delete selected URL
    #     # urls = [url for url in urls if not url.name == 'delete_selected']
        
    #     # # Remove the history URL
    #     # urls = [url for url in urls if not url.name == 'history']
        
    #     # Add your own custom URL patterns here
        
    #     return urls

    def index(self, request, extra_context=None):
        # Your custom index view logic here
        extra_context = None
        print("*******My Admin Site Index*******")
        # if request.user.is_authenticated:
        
        return super().index(request, extra_context)
        MyLoginView.as_view()(request)

        
    
    def login(self, request, extra_context=None):
        print("My Admin Site login")
        if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
            # User is already logged in, redirect them to the admin index page
            return HttpResponseRedirect(reverse('admin:index'))
        elif request.user.is_authenticated:
            print("redirecting normal user to home")
            return HttpResponseRedirect(reverse('home'))
        else:
            # User is not logged in, redirect them to your custom login page
            return MyLoginView.as_view()(request)
        
    # def logout(self, request, extra_context=None):
    #     return super().logout(request, None)



# Create an instance of the custom AdminSite class
my_admin_site = MyAdminSite(name='myadmin')


# Create your views here.
