from .admin import my_admin_site
from core.healthcare.admin import my_doctor_site
from django.urls import re_path


urlpatterns = [
    re_path(r'^admin/', my_admin_site.urls, name="admin-dashboard"),
    re_path(r'^doctor/', my_doctor_site.urls, name="doctor-dashboard"),
]