from django.contrib import admin, messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import admin
from core.healthcare.admin import my_doctor_site
from core.my_admin.admin import my_admin_site
from .models import Booking
from core.healthcare.models import UsersMedicalRecord

class BookingAdmin(admin.ModelAdmin):
    change_form_template = 'admin/booking_change.html'
    list_filter = ("appointment_date_time",)


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Superusers can see all diagnostic corrections
        current_doctor = request.user
        if current_doctor:
            return qs.filter(doctor_id=current_doctor.id)
        return qs.none()  # Return an empty queryset if the user is not a doctor or doesn't have any bookings
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        booking = self.get_object(request, object_id)
        if hasattr(booking.subject, "UsersMedicalRecord"):
            users_medical_record = booking.subject.UsersMedicalRecord
        
            # Add the UsersMedicalRecord to the extra_context
            extra_context = extra_context or {}
            extra_context['users_medical_record'] = users_medical_record
            print(extra_context['users_medical_record'])
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        booking = self.get_object(request, object_id)
        if hasattr(booking.subject, "usersmedicalrecord"):
            users_medical_record = booking.subject.usersmedicalrecord

            # Add the UsersMedicalRecord to the extra_context
            extra_context = extra_context or {}
            extra_context['users_medical_record'] = users_medical_record

        # Handle the save button action
        if request.method == 'POST' and '_save' in request.POST:
            if not self.has_change_permission(request, booking):
                return self.response_change(request, booking)
            return HttpResponseRedirect(request.path)

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)
        
    def response_change(self, request, obj):
        opts = obj._meta
        pk_value = obj._get_pk_val()
        preserved_filters = self.get_preserved_filters(request)
        msg = 'Changes saved successfully.'
        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(
            reverse('admin:%s_%s_change' % (opts.app_label, opts.model_name),
                    args=(pk_value,),
                    current_app=self.admin_site.name,
            )
        )



#admin site
my_admin_site.register(UsersMedicalRecord)
my_admin_site.register(Booking)



#doctor site
# my_doctor_site.register(Booking)

my_doctor_site.register(Booking, BookingAdmin)

