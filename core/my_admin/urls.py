from .admin import my_admin_site, my_user_site
from core.healthcare.admin import my_doctor_site
from django.urls import re_path
from django.http import HttpResponseNotFound


def catch_all_view(request):
    return HttpResponseNotFound("Page not found")

urlpatterns = [
    re_path(r'^admin/', my_admin_site.urls, name="admin-dashboard"),
    re_path(r'^doctor/', my_doctor_site.urls, name="doctor-dashboard"),
    re_path(r'^user/', my_user_site.urls, name="user-dashboard"),
    # re_path(r'^(?P<url>.*)$', catch_all_view),

]