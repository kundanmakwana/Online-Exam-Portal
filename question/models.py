from django.db import models
class question(models.Model):
    id = models.BigAutoField(primary_key=True)
    q_text = models.CharField(max_length=255)
    op_a = models.CharField(max_length=255)
    op_b = models.CharField(max_length=255)
    op_c = models.CharField(max_length=255)
    op_d = models.CharField(max_length=255)
    ans = models.CharField(max_length=255)
    b_id = models.CharField(max_length=10)
    e_id = models.CharField(max_length=10)
# Create your models here.
