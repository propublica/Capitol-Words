from django.db import models

# Create your models here.

class CongressionalRecordVolume(models.Model):
    congress = models.IntegerField(db_index=True)
    session = models.CharField(max_length=10, db_index=True)
    volume = models.IntegerField()
