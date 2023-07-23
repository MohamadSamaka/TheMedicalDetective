from django import forms
from core.healthcare.models import UsersMedicalRecord
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, Div
from ...models import CustomUser
from django.utils.safestring import mark_safe



class UserMedicalInformation(forms.ModelForm):
    class Meta:
        model = UsersMedicalRecord
        exclude = ['user', 'gender']
        widgets = {
            'bdate': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Medical Information',
                Div(
                    Row(
                        Column('height', css_class='col-md-6'),
                        Column('weight', css_class='col-md-6'),
                        css_class='form-row'
                    ),
                    Row(
                        Column('bdate', css_class='col-md-6'),
                        Column('phone_num', css_class='col-md-6'),
                        css_class='form-row'
                    ),
                    Row(
                        Column('city', css_class='col-md-6'),
                        Column('blood_type', css_class='col-md-6'),
                    ),
                    css_class='form-group'
                ),
                Submit('submit', 'save')
            )
        )


class UserGeneralInformation(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Genetal Information',
                Div(
                    Row(
                        Column('first_name', css_class='col-md-6'),
                        Column('last_name', css_class='col-md-6'),
                        css_class='form-row'
                    ),
                    Row(
                        Column('email', css_class='col-md-6'),
                        css_class='form-row'
                    ),
                ),
                Submit('submit', 'save', css_id="update-general-info-btn"),
            )
        )