from django import forms
from django.urls import reverse_lazy
from  django.contrib.auth import get_user_model
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from datetime import datetime, timedelta


class BookingInfoForm(forms.Form):
    doc = forms.ChoiceField(
        choices=[], 
        required=True,
        )
    appointment_date_time = forms.DateTimeField(
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doc'].choices = self.get_all_doc_ids()

    def get_all_doc_ids(self):
        docs_ids = get_user_model().objects.filter(groups__name="doctor").values_list('id', flat=True)
        choices = [(str(doc_id), str(doc_id)) for doc_id in docs_ids]
        return choices
