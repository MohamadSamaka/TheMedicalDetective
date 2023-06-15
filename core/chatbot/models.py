from django.db import models
from django.conf import settings

class BotDiagnoses(models.Model):
    symptoms_group = models.ManyToManyField(
        'healthcare.Symptoms',
    )

    diagnosis = models.ForeignKey(
        'healthcare.Diseases',
        on_delete=models.CASCADE,
    )

    diagnosis_date = models.DateField(null=False, blank=False)
    diagnosis_time = models.TimeField(null=False, blank=False)

    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )