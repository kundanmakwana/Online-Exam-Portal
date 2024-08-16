from django.contrib import admin
from result.models import result
# Register your models here.
class ReslutAdmin(admin.ModelAdmin):
    list_display = ('s_id','e_id','marks_obt','total_marks','perct')
    
admin.site.register(result,ReslutAdmin)
