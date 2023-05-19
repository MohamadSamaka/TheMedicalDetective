from django.contrib import admin

# Register your models here.

from .models import UsersMeicalRecord
from ..myAdmin.views import my_admin_site


my_admin_site.register(UsersMeicalRecord)