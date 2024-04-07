from django.db import models
from django.conf import settings

# Create your models here.
class seatModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roomNum = models.IntegerField()
    seatNum = models.IntegerField()

