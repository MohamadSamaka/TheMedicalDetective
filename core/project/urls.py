"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.contrib.auth import views as auth_views #new
from django.urls import path, include, re_path
# from core.home.views import Consumer
# from ..healthcare.models import UsersPersonalMecicalInfomatrion
from core.home.consumers import Consumer
from django.conf import settings
from django.conf.urls.static import static
from django.views import static as django_static
from django.views.static import serve  # Import the serve function


import re

# admin.register(UsersPersonalMecicalInfomatrion)

from django.conf import settings
from django.http import Http404
from django.views.static import serve

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
import os
import re

# def custom_serve(request, path, document_root=None, show_indexes=False):
#     excluded_directories = ['protected', 'datasets', 'hidden']

#     normalized_path = path.lstrip('/')
#     for directory in excluded_directories:
#         if normalized_path.startswith(directory + '/'):
#             # Exclude the directory from being served
#             raise Http404('File not found')

#     # Call the original serve function to serve the media file
#     return serve(request, path, document_root, show_indexes)
    



urlpatterns = [
    path('', include('core.home.urls')),
    path('', include('core.clinics.urls')),
    path('', include('core.authentication.urls')),
    path('', include('core.my_admin.urls')),
    path('', include('core.core.urls')),
    re_path(r'ws/socket-server/', Consumer),
    path('home/', include('core.home.urls')),
    path('chatbot/', include('core.chatbot.urls')),
    path('booking/', include('core.booking.urls')),

    # path('admin/', my_admin_site.urls),

    # path('admin/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'), #new
    # path('admin/', admin.site.urls),
    # path('login/', MyLoginView.as_view(), name='login'),
    # path('myadmin/', my_admin_site.urls)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
