from django.db import models


# Create your models here.
class eventModel(models.Model):
    date = models.PositiveBigIntegerField(primary_key=True)
    eventName = models.CharField(max_length=30)
    type = models.CharField(max_length=15)
