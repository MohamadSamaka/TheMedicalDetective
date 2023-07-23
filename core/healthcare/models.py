from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


BLOOD_TYPE_CHOICES = {
    1 : 'A+',
    2 : 'A-',
    3 : 'B+',
    4 : 'B-',
    5 : 'O+',
    6 : 'O-',
    7 : 'AB+',
    8 : 'AB-'
}


DAYS_MAP = {
    1 : 'Monday',
    2 : 'Tuesday',
    3 : 'Wednesday',
    4 : 'Thursday',
    5 : 'Friday',
    6 : 'Saturday',
    7 : 'Sunday',
}


class UsersMedicalRecord(models.Model):
    """
    Model to store the personal medical information of the user
    """
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=False,
        null=False,
        verbose_name="Height in meters",
        validators=[MinValueValidator(24.0), MaxValueValidator(251.0)]
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=False, 
        null=False,
        verbose_name="Weight in kilograms",
        validators=[MinValueValidator(20.0), MaxValueValidator(635.0)]
    )
    blood_type = models.IntegerField(choices=BLOOD_TYPE_CHOICES.items(), blank=False, null=False, verbose_name="Blood Type")
    bdate = models.DateField(verbose_name="Date of Birth")
    gender = models.BooleanField(blank=False, null=False, verbose_name="Gender")
    city = models.ForeignKey(
        'core.City',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="City"
    )
    phone_num = models.CharField(max_length= 10, blank=False, null=False, verbose_name="Phone Number")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def validate_blood_type(self):
        if self.blood_type not in BLOOD_TYPE_CHOICES:
            raise ValidationError(
                ('%(value)s is not a valid blood type'),
                params={'value': self.blood_type},
            )
    
    def save(self, *args, **kwargs):
        self.validate_blood_type()
        super().save(*args, **kwargs)

    # def clean(self):
    #     print("the height is: ", self.height)
    #     if self.height < 0.0 or self.height > 100.0:
    #         raise ValidationError("Height must be between 0.0 and 100.0.")

    def __str__(self):
        # print(self.medical_record.first_name)
        return f"{self.user.first_name} {self.user.last_name}"


class Symptoms(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name.replace('_', ' ')


class Diseases(models.Model):
    name = models.CharField(max_length=45)

    specializations = models.ManyToManyField(
        'healthcare.Specializations',
        verbose_name="Treater Specialization"
    )

    purifications = models.ManyToManyField(
        'healthcare.Purifications',
        verbose_name="Purifications"
    )

    def __str__(self):
        return self.name
    

class Purifications(models.Model):
    description = models.CharField(max_length=45)
    


class Hospitals(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(
        max_length=50,
        verbose_name="Address"
    )

    image = models.ImageField(
        null=True,
        blank=True,
        default="images/hospitals/default_hospital.png",
        upload_to="images/hospitals"
    )

    city = models.ForeignKey(
        'core.City',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="City"
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Phone"
    )
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.name


class Specializations(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Name"
    )

    def __str__(self):
        return self.name


class DoctorsInformation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    image = models.ImageField(
        null=True,
        blank=True,
        default="images/doctors/default_doctor.png",
        upload_to="images/doctors"
    )

    hospitals = models.ForeignKey(
        Hospitals,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Information"
    )

    specialization = models.ForeignKey(
        Specializations,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        verbose_name="Specialization"
    )

    competence = models.DecimalField(
        blank=False,
        null=False,
        max_digits=5,
        decimal_places=2,
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Phone"
    )
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    day_of_week = models.IntegerField(choices=DAYS_MAP.items())

    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('doctor', 'day_of_week')

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{str(self.doctor)} | {DAYS_MAP[self.day_of_week]}"


class DoctorUnavailable(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    day_of_week = models.IntegerField(choices=DAYS_MAP.items())

    class Meta:
        unique_together = ('doctor', 'day_of_week')

    def __str__(self):
        return f"{str(self.doctor)} | {DAYS_MAP[self.day_of_week]}"