from django.db import models

# Create your models here.
class Logger(models.Model):
    fd_title = models.CharField(max_length=31)
    fd_text = models.CharField(max_length=255)
    fd_time = models.DateTimeField(auto_now=True)

