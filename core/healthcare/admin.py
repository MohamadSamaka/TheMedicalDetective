from .models import UsersMeicalRecord, Symptoms, Diseases
from core.my_admin.views import my_admin_site

my_admin_site.register(UsersMeicalRecord)
my_admin_site.register(Symptoms)
my_admin_site.register(Diseases)