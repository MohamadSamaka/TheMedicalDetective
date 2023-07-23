from core.my_admin.admin import my_admin_site
from .models import Symptoms, Diseases, Purifications, DoctorsInformation, DoctorSchedule, DoctorUnavailable, Hospitals
from core.core.admin import BaseAdminSite
from django.contrib.admin import ModelAdmin
from django.db import models



class MyDoctorSite(BaseAdminSite):
    site_header = 'Doctor Dashboard'
    site_title = 'Doctor Dashboard'
    index_title = 'Doctor Dashboard'
    site_name = 'doctor-site'  # Unique namespace for the doctor admin site


class DoctorScheduleAdmin(ModelAdmin):
    # Your customizations for the admin class go here
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time']
    list_filter = ['day_of_week']
    search_fields = ['doctor__first_name', 'doctor__last_name', 'day_of_week']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_authenticated:
            return qs.filter(doctor=request.user)
        else:
            return qs.none()
        
class DoctorUnavailableAdmin(ModelAdmin):
    list_display = ['doctor', 'day_of_week']
    list_filter = ['day_of_week']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_authenticated:
            # Filter unavailable days based on the currently logged-in doctor
            return qs.filter(doctor=request.user)
        else:
            # Return an empty queryset if no doctor is logged in
            return qs.none()



my_admin_site.register(Hospitals)
my_admin_site.register(Symptoms)
my_admin_site.register(Diseases)
my_admin_site.register(Purifications)
my_admin_site.register(DoctorsInformation)
my_admin_site.register(DoctorSchedule)
my_admin_site.register(DoctorUnavailable)


my_doctor_site = MyDoctorSite(name="adminpage-doctor")


my_doctor_site.register(DoctorSchedule, DoctorScheduleAdmin)
my_doctor_site.register(DoctorUnavailable, DoctorUnavailableAdmin)