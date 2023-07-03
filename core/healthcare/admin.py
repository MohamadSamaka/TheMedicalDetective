from django.contrib.admin import AdminSite
from core.my_admin.admin import my_admin_site
from .models import Symptoms, Diseases


class MyDoctorSite(AdminSite):
    site_header = 'Doctor Dashboard'
    site_title = 'Doctor Dashboard'
    index_title = 'Doctor Dashboard'
    site_name = 'doctor-site'  # Unique namespace for the doctor admin site


my_admin_site.register(Symptoms)
my_admin_site.register(Diseases)

my_doctor_site = MyDoctorSite(name="adminpage-doctor")