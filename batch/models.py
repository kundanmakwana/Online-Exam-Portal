from django.db import models
class batch(models.Model):
    id = models.BigAutoField(primary_key=True)
    b_id=models.CharField(max_length=10)
    b_name=models.CharField(max_length=100)
    s_id=models.CharField(max_length=10)
    t_id=models.CharField(max_length=10)
# Create your models here.
