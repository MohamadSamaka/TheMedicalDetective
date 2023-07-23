from django.contrib.admin import AdminSite

class BaseAdminSite(AdminSite):
    login_template = 'authentication/pages/log-in.html'


from .models import City
from core.my_admin.admin import my_admin_site
my_admin_site.register(City)