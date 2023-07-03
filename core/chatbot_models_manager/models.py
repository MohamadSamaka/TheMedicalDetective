from django.db import models

class Diagnoser(models.Model):
    model_name = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
    )
    
    def __str__(self):
        return self.model_name

class NER(models.Model):
    model_name = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.model_name
