from django.db import models

# Create your models here.
class notify(models.Model):
    id = models.BigAutoField(primary_key=True)
    b_id = models.CharField(max_length=10)
    notify_text = models.CharField(max_length=255)
    notify_time = models.CharField(max_length=255)