from .views import my_admin_site
from django.urls import path


urlpatterns = [
    path('admin/', my_admin_site.urls, name="admin-dashboard"),
]
