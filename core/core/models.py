# from blogsite.models import Post
# from blogsite.models import Comment
from django.db import models

class City(models.Model):
    name = models.CharField(blank=False, null=False, max_length=25)

    def __str__(self):
        return f'{self.name}'