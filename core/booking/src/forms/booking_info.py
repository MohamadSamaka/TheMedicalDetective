from django import forms
from django.urls import reverse_lazy
from  django.contrib.auth import get_user_model
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from datetime import datetime, timedelta

class BookingInfoForm(forms.Form):
     
    def __init__(self, *args, **kwargs):
        from ...models import Booking
        booked_appointments = [dt.strftime("%Y-%m-%dT%H:%M:%S.%f") for dt in Booking.objects.values_list('appointment_date_time', flat=True)]
        # print("disabled: ", booked_appointments)
        super().__init__(*args, **kwargs)
        self.fields['doc'].choices = self.get_all_doc_ids()
        if True:
                # print("origin: ", [datetime.now().isoformat(), (datetime.now() + timedelta(hours=48)).isoformat()])
                # print("booked:", booked_appointments)
                # print("converted:", booked_appointments[:2])
                # default_options = self.fields['appointment_date_time'].widget.options
                # default_options={
                #       'format': 'YYYY-MM-DD hh:mm A',
                #         'stepping': 20,
                #         'minDate': datetime.now(),
                #         # 'disabledTimeIntervals': booked_appointments[:2]
                # }
                # print(booked_appointments[:2][::-1])
                self.fields['appointment_date_time'].widget = DateTimePickerInput(
                    options={
                        'format': 'YYYY-MM-DD hh:mm A',
                        'stepping': 15,
                        'minDate': datetime.now(),
                        'disabledTimeIntervals':[
                            #  ['2023-06-15T00:38:51.511211', '2023-06-24T00:38:51.511211'],
                            # booked_appointments[:2]
                            # [datetime.now().isoformat(), (datetime.now() + timedelta(days=4, hours=1)).isoformat()]
                        ]
                    }
                )
                # default_options.update({
                #     'disabledTimeIntervals': booked_appointments[:2],
                # })
                # # .options['disabledTimeIntervals'] = booked_appointments[:2]
                # self.fields['appointment_date_time'].widget.options["disabledTimeIntervals"] = [
                #     booked_appointments[:2]
                # ]
 


    doc = forms.ChoiceField(choices=[])

    appointment_date_time = forms.DateTimeField(
        widget=DateTimePickerInput(
            # options={
            #     'format': 'YYYY-MM-DD hh:mm A',
            #     'stepping': 15,
            #     'minDate': datetime.now(),
            #     # 'daysOfWeekDisabled': [0,3],
            #     # 'disabledTimeIntervals':
            #     # [
            #     #     [datetime.now().isoformat(), (datetime.now() + timedelta(hours=1)).isoformat()]
            #     # ],
                
            # }
        )
    )

    def get_all_doc_ids(self):
        docs_ids = get_user_model().objects.filter(groups__name="doctor").values_list('id', flat=True)
        choices = [(str(doc_id), str(doc_id)) for doc_id in docs_ids]
        return choices