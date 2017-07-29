from django.db import models


class CRECScraperResult(models.Model):

    date = models.DateField()
    success = models.BooleanField()
    message = models.TextField()
    num_crec_files_uploaded = models.IntegerField(default=0)
