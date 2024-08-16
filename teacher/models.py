from django.db import models
class teacher(models.Model):
    id = models.BigAutoField(primary_key=True)
    t_name=models.CharField(max_length= 50)
    t_email=models.CharField(max_length=100)
    t_password=models.CharField(max_length=100)
    t_id=models.CharField(max_length=10)
    t_pfp = models.ImageField(upload_to='t_pfps',default="Default_pfp.png")
    t_is_logged_in = models.CharField(max_length=255)
    t_remember = models.CharField(max_length=255)
    ha_id = models.CharField(max_length=10)
# Create your models here.
