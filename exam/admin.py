from django.contrib import admin
from exam.models import exam
# Register your models here.
class ExamAdmin(admin.ModelAdmin):
    list_display = ('e_name','e_q_num','e_marks','t_id','st_time','end_time')
    
admin.site.register(exam,ExamAdmin)