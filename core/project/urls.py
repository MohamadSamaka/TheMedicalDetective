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
from django.urls import path, include

# from ..healthcare.models import UsersPersonalMecicalInfomatrion


# admin.register(UsersPersonalMecicalInfomatrion)

urlpatterns = [
    path('', include('core.home.urls')),
    path('home/', include('core.home.urls')),
    path('chatbot/', include('core.chatbot.urls')),
    # path('', include('core.chatbot.urls')),
    path('', include('core.authentication.urls')),
    path('', include('core.myAdmin.urls')),



    # path('admin/', my_admin_site.urls),

    # path('admin/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'), #new
    # path('admin/', admin.site.urls),
    # path('login/', MyLoginView.as_view(), name='login'),
    # path('myadmin/', my_admin_site.urls)
]
