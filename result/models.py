from django.db import models
class result(models.Model):
    id = models.BigAutoField(primary_key=True)
    s_id = models.CharField(max_length=10)
    e_id = models.CharField(max_length=10)
    marks_obt = models.IntegerField()
    total_marks = models.IntegerField()
    perct = models.CharField(max_length=10)
# Create your models here.
