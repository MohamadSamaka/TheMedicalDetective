from django.db import models
from django.conf import settings

class Booking(models.Model):
    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=['appointment_date_time', 'doctor_id'],
            name='unique_appointment_doctor'
        ),
        models.UniqueConstraint(
            fields=['appointment_date_time', 'subject_id'],
            name='unique_appointment_subject'
        ),
    ]

    subject = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subject_booking'
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_booking'
    )

    bot_diagnosis = models.ForeignKey(
        'chatbot.BotDiagnoses',
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        default=None
    )

    appointment_date_time = models.DateTimeField(
        null=False,
        blank=False,
    )
    # appointment_date = models.DateField(null=False, blank=False)
    # appointment_time = models.TimeField(null=False, blank=False)
    appointment_completion_time = models.TimeField(
        null=True,
        blank=False,
        default=None
    )

    def __str__(self):
        return "%s %s"%(self.subject.first_name, self.subject.first_name)

