from django.contrib import admin
from feedback.models import feedback
# Register your models here.
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('email','subject','message')
    
admin.site.register(feedback,FeedbackAdmin)