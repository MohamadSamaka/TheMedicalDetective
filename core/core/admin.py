from django.apps import apps
from .models import City
from ..my_admin.views import my_admin_site

my_admin_site.register(City)