from django.contrib import admin
from student.models import student
# Register your models here.
class StudentAdmin(admin.ModelAdmin):
        list_display = ('s_name','s_email','s_password','s_id')
        
admin.site.register(student,StudentAdmin)
