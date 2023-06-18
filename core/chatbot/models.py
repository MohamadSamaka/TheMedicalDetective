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

    def __str__(self):
        return f"{self.diagnosis.name}"
    

class DiagnosticCorrector(models.Model):
    bot_diagnosis = models.ForeignKey(
        'chatbot.BotDiagnoses',
        on_delete=models.CASCADE
    )
    
    symptoms_group = models.ManyToManyField(
        'healthcare.Symptoms',
    )

    diagnosis = models.ForeignKey(
        'healthcare.Diseases',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.bot_diagnosis.subject)