from django.db import models

# Create your models here.
class HeadAdmin(models.Model):
    id = models.BigAutoField(primary_key=True)    
    h_id = models.CharField(max_length=10)
    h_name=models.CharField(max_length= 50)
    h_email=models.CharField(max_length=100)
    h_password=models.CharField(max_length=100)
    h_pfp = models.ImageField(upload_to='t_pfps',default="Default_pfp.png")
    h_is_logged_in = models.CharField(max_length=255)
    h_remember = models.CharField(max_length=255)
    
    