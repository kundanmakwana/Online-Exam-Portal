from django.contrib import admin
from batch.models import batch
# Register your models here.

class BatchAdmin(admin.ModelAdmin):
    list_display = ('b_id','s_id','t_id')
    
admin.site.register(batch,BatchAdmin)