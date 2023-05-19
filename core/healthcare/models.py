from django.db import models
from django.core.exceptions import ValidationError
from core.project import settings


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


class UsersMeicalRecord(models.Model):
    """
    Model to store the personal medical information of the user
    """
    # from ..core.models import City, CustomUser
    from ..core.models import City
    # id = models.BigAutoField(primary_key=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False, verbose_name="Height in meters")
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False,verbose_name="Weight in kilograms")
    blood_type = models.IntegerField(choices=BLOOD_TYPE_CHOICES.items(), blank=False, null=False, verbose_name="Blood Type")
    bdate = models.DateField(verbose_name="Date of Birth")
    gender = models.BooleanField(blank=False, null=False, verbose_name="Gender")
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=False, null=False, verbose_name="City")
    phone_num = models.CharField(max_length= 10, blank=False, null=False, verbose_name="Phone Number")



    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    # user = models.ForeignKey(
    #     CustomUser,
    #     on_delete=models.CASCADE,
    #     null=True,
    # )

    def validate_blood_type(self):
        if self.blood_type not in BLOOD_TYPE_CHOICES:
            raise ValidationError(
                ('%(value)s is not a valid blood type'),
                params={'value': self.blood_type},
            )
    
    def save(self, *args, **kwargs):
        self.validate_blood_type()
        super().save(*args, **kwargs)

    def __str__(self):
        # print(self.medical_record.first_name)
        return f"{self.user.first_name} {self.user.last_name}"

