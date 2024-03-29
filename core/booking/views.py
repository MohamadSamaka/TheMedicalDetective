from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Prefetch
from django.http import JsonResponse, HttpResponse
from core.healthcare.models import Hospitals, Specializations, DoctorSchedule, DoctorUnavailable, DoctorsInformation
# from .src.forms.forms import BookingFiltersForm, BookingInfoForm
from .src.forms.booking_filters import BookingFiltersForm
from .src.forms.booking_info import BookingInfoForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from itertools import groupby
from operator import itemgetter
import json
from datetime import datetime


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class BookingView(TemplateView):
    template_name = 'client/pages/booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specelization_map'] = self.get_specializations_map()
        context['hospitals_docs'] =  self.get_docs_per_hospital_info()
        context['booking_filters_form'] = BookingFiltersForm()
        context['booking_info_form'] = BookingInfoForm()
        context['url_name'] = self.request.resolver_match.app_name
        return context
    
    # def get_context_data(self, **kwargs):
    #     # booking_info = self.request.session.get('booking_info')
    #     context = super().get_context_data(**kwargs)
    #     context['specelization_map'] = self.get_specializations_map()
    #     context['hospitals_docs'] =  self.get_docs_per_hospital_info()
    #     context['booking_filters_form'] = BookingFiltersForm()
    #     context['booking_info_form'] = BookingInfoForm()
    #     context['url_name'] = self.request.resolver_match.app_name
    #     # context['recomanded_doctor_id'] = None if booking_info is None else booking_info['recomanded_doctor_id']
    #     return context
    
    
    def post(self, request):
        from django.utils import timezone
        booking_info = request.session.pop('booking_info', None)
        diagnosis_id = booking_info["diagnosis_id"] if booking_info else None
        # recomanded_doctor_id = booking_info["recomanded_doctor_id"] if booking_info else None
        if request.method != "POST":
            return JsonResponse({"status": "error", "message": "Invalid request method"}, status=500)
        try:
            doc_id = request.POST.get('doc-id')
            parsed_date_time = self.parse_date_time(request.POST.get('date-time'))
            form_data = {
                'doc': doc_id,
                'appointment_date_time': parsed_date_time,
                # 'recomanded_doctor': recomanded_doctor_id
            }
           
            booking_form = BookingInfoForm(form_data)
            if not booking_form.is_valid():
                return HttpResponse(booking_form.errors.as_json(), status=400)
            self.validate_date_time(parsed_date_time)
            parsed_date_time = timezone.make_aware(parsed_date_time).replace(second=0, microsecond=0)
            return self.book_appointment(request.user.id, parsed_date_time, doc_id, diagnosis_id)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Please send an appropriate date and time!"}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "message": "Something went wrong! Please try again"}, status=400)
            
    

    def parse_date_time(self, date_time):
        date_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M').replace(second=0, microsecond=0)
        return date_time
    
    def validate_date_time(self, sent_date_time):
        stepping = 15
        curr_date_time = datetime.now().replace(second=0, microsecond=0)
        if sent_date_time <= curr_date_time:
            raise ValueError
        else:
            minute = sent_date_time.minute
            # duplicate_rows = Booking.objects.values('appointment_date_time').annotate(count=Count('timestamp')).filter(count__gt=1)
            if minute % stepping != 0:
                raise ValueError
        print("cool!")
            
            
    def book_appointment(self, subject_id, date_time, doc_id, bot_diagnosis_id=None):
        from .models import Booking
        from core.chatbot.models import BotDiagnoses
        from django.db import IntegrityError
        try:
            subject = get_user_model().objects.get(id=subject_id)
            doctor = get_user_model().objects.get(id=doc_id)
            bot_diagnosis = BotDiagnoses.objects.get(id=bot_diagnosis_id) if bot_diagnosis_id else None
            booking = Booking.objects.create(
                subject=subject,
                doctor=doctor,
                appointment_date_time = date_time,
                bot_diagnosis = bot_diagnosis,
            )
            booking.save()
        except IntegrityError as e:
            error_message = str(e)
            return JsonResponse({
                "status": "error",
                "message": "Sorry this appointment slot has already been reserved, please pick another date/time." if "unique_appointment_doctor" in error_message
                else "You already have an appointment at this day and time, Please pick another date/time."
                },
                status=409
            )
        
        return JsonResponse({"status": "success", "message": "Appointment been booked successfully"})
    
    
    def get_specializations_map(self):
        specs = list(Specializations.objects.all().values())
        return json.dumps({s["id"]: s["name"] for s in specs})
    

    def get_docs_per_hospital_info(self):
        from django.core.serializers import serialize
        from django.core.serializers.json import DjangoJSONEncoder

        from datetime import time  # Import the time class from datetime module
        hospital_doctors = Hospitals.objects.prefetch_related(
            Prefetch(
                'doctorsinformation',
                queryset=[
                    get_user_model().objects.only('first_name', 'last_name'),
                ]
            )
        ).annotate(
            num_doctors=models.Count('doctorsinformation'),
        ).filter(
            num_doctors__gt=0).values_list(
            'id',
            'city',
            'doctorsinformation__hospitals__name',
            'doctorsinformation__image',
            'doctorsinformation__user',
            'doctorsinformation__user__first_name',
            'doctorsinformation__user__last_name',
            'doctorsinformation__specialization',
            
        )

        grouped_data = groupby(hospital_doctors, itemgetter(0, 1, 2)) 
        print(hospital_doctors[0])
        def serialize_time(obj):
            if isinstance(obj, time):
                return obj.strftime('%H:%M:%S')
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


        docs_per_hospitals = {}
        for (hospital_id, city_id, hospital_name), values in grouped_data:
            docs_per_hospitals[hospital_id] = {
                'hospital_name': hospital_name,
                'city': city_id,
                'docs': []
            }
            for doc_info in values:
                doctor = {
                    'id': doc_info[4],
                    'image': doc_info[3],
                    'f_name': doc_info[5],
                    'l_name': doc_info[6],
                    'specialization': doc_info[7],
                    'schedules': [],
                    'unavailabilities': []
                }

                schedules = DoctorSchedule.objects.filter(
                    doctor=doc_info[4]
                ).only('day_of_week', 'start_time', 'end_time')
                for schedule in schedules:
                    doctor['schedules'].append({
                        'day_of_week': schedule.day_of_week,
                        'start_time': schedule.start_time,
                        'end_time': schedule.end_time,
                    })

                unavailabilities = DoctorUnavailable.objects.filter(
                    doctor=doc_info[4]
                ).only('day_of_week')
                for unavailability in unavailabilities:
                    doctor['unavailabilities'].append(unavailability.day_of_week)

                docs_per_hospitals[hospital_id]['docs'].append(doctor)


        serialized_data = json.dumps(docs_per_hospitals, default=serialize_time)

        return serialized_data
        # return json.dumps(docs_per_hospitals)    

initBookingView = BookingView()