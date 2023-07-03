from django.contrib.auth.models import Group
from .models import City

from core.my_admin.admin import my_admin_site
my_admin_site.register(City)