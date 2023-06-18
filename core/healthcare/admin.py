from django.contrib import admin
from core.core.admin import BaseAdminSite
from core.my_admin.admin import my_admin_site
from .models import UsersMeicalRecord, Symptoms, Diseases
from core.booking.models import Booking
from core.chatbot.models import DiagnosticCorrector


class MyDoctorSite(BaseAdminSite):
    site_header = 'Doctor Dashboard'
    site_title = 'Doctor Dashboard'
    index_title = 'Doctor Dashboard'


my_admin_site.register(Symptoms)
my_admin_site.register(Diseases)

my_doctor_site = MyDoctorSite(name="adminpage-doctor")