from django.db import models
class student(models.Model):
    id = models.BigAutoField(primary_key=True)
    s_name=models.CharField(max_length= 50)
    s_email=models.CharField(max_length=100)
    s_password=models.CharField(max_length=100)
    s_id=models.CharField(max_length=10)
    s_pfp = models.ImageField(upload_to='s_pfps',default="Default_pfp.png")
    s_is_logged_in = models.CharField(max_length=255)
    s_remember = models.CharField(max_length=255)
# Create your models here.
