from django.contrib import admin
from question.models import question
# Register your models here.
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('q_text','op_a','op_b','op_c','op_d','ans','b_id')
    
admin.site.register(question,QuestionAdmin)