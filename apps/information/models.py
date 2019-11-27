from django.contrib.auth.models import User
from django.db import models


class News(models.Model):
    title = models.CharField(max_length=100, null=True)
    text = models.CharField(max_length=1000)
    time = models.DateTimeField()

