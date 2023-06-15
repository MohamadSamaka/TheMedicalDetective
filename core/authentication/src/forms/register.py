from django import forms
from django.http import HttpResponse
from django.core.validators import RegexValidator
from django.core.validators import validate_slug, validate_unicode_slug
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from datetime import datetime

name_rule = r'^[a-zA-Z]+$'
name_validator = RegexValidator(
    regex=name_rule,
    message='Name can only contain letters',
)

phone_rule = r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
name_validator = RegexValidator(
    regex=phone_rule,
    message='phone can only contain numbers',
)

validationRules = {
	'fname': r'^[a-zA-Z]{1,25}$',
	'lname': r'^[a-zA-Z]{1,25}',
	'email': None,
	#'pass': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{10,}',
	'pass': r'^.{10,}',
	# 'confirm-pass': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{10,}',
	'confirm-pass': r'^.{10,}',
	'phone-num': r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}',
    'bdate': None,
    'height': None,
    'weight': None,
    'blood-type': None,
    'gender': None,
    'city': None,
    }


class SignUpForm(forms.Form):
    from core.core.models import City
    from core.my_admin.models import CustomUser
    from core.healthcare.models import UsersMeicalRecord, BLOOD_TYPE_CHOICES
    email = forms.EmailField()
    password = forms.CharField(min_length=10, widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=25, validators=[validate_unicode_slug], required=True)
    last_name = forms.CharField(max_length=25, validators=[validate_unicode_slug], required=True)
    phone_num = forms.CharField(max_length=15, validators=[validate_slug ], required=True)
    height = forms.DecimalField(max_digits=5, decimal_places=2, required=True)
    weight = forms.DecimalField(max_digits=5, decimal_places=2, required=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=True)
    blood_type =  forms.ChoiceField(choices=BLOOD_TYPE_CHOICES.items(), required=True)
    bdate = forms.DateField(required=True)
    gender = forms.CharField(widget=forms.RadioSelect(choices=[(True, '0'), (False, '1')]), required=False)

    def calculate_age(self, bdate):
        today = datetime.today()
        age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
        return age

    def clean_bdate(self):
        bdate = self.cleaned_data['bdate']
        age = self.calculate_age(bdate)
        if age > 120 or age <= 6:
            raise ValidationError("You must be between 6 and 120 years old to register")
        return bdate

    @transaction.atomic
    def save(self):
        try:
            user = self.CustomUser.objects.create(
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                password=make_password(self.cleaned_data['password']), # Hash password before saving,
            )
            # create a new medical record object
            self.UsersMeicalRecord.objects.create(
                user=user,
                phone_num=self.cleaned_data['phone_num'],
                height=self.cleaned_data['height'],
                weight=self.cleaned_data['weight'],
                city=self.cleaned_data['city'],
                blood_type=int(self.cleaned_data['blood_type']),
                bdate=self.cleaned_data['bdate'],
                gender=bool(int(self.cleaned_data['gender'])),
            )
        except IntegrityError as e:
            if e.args[0] == 1062: #duplicate entry error
                print("duplicate will be called now:")
                return HttpResponse("This email is already taken", status=400)
            else:
                print("exception caught:", e)
                return HttpResponse("Something went wrong, try again later", status=400)
        return HttpResponse("email confirmed")
    # code = forms.CharField(max_length=10)
