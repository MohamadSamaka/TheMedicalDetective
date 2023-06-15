from django import forms
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from core.healthcare.models import Specializations, Hospitals


class BookingFiltersForm(forms.Form):
    # search = forms.CharField(
    #     label=False,
    #     widget=forms.TextInput(
    #     attrs={'placeholder': 'Search'}
    #     )
    # )
    # city = forms.ModelChoiceField(
    #     queryset=City.objects.all(),
    #     empty_label='Select a city',
    #     widget=forms.Select(attrs={'class': 'custom-select'}),
    # )
    hospitals = forms.ModelChoiceField(
        queryset=Hospitals.objects.all(),
        empty_label='Select a hospital',
        widget=forms.Select(attrs={'class': 'custom-select'}),
    )
    specialization = forms.ModelMultipleChoiceField(
        queryset=Specializations.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'filters-form'
        self.helper.form_method = 'POST'
        self.helper.form_action = reverse_lazy('home')
        print(self.helper.form_id)