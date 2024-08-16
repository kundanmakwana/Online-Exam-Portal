from django.contrib import admin
from teacher.models import teacher
# Register your models here.

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('t_name','t_email','t_password','t_id')
    
admin.site.register(teacher,TeacherAdmin)
