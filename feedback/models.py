from django.db import models

# Create your models here.
class feedback(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()