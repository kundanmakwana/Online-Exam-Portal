from django.db import models
class exam(models.Model):
    id = models.BigAutoField(primary_key=True)
    e_name = models.CharField(max_length=100)
    e_q_num = models.IntegerField()
    e_marks = models.IntegerField()
    t_id = models.CharField(max_length=10)
    e_id = models.CharField(max_length=10)
    b_id = models.CharField(max_length=10)
    b_name=models.CharField(max_length=100)    
    st_time = models.CharField(max_length=255)
    end_time = models.CharField(max_length=255)
    
# Create your models here.
