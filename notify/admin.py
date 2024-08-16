from django.contrib import admin
from notify.models import notify
# Register your models here.
class NotifyAdmin(admin.ModelAdmin):
    list_display = ('b_id','notify_text','notify_time')
    
admin.site.register(notify,NotifyAdmin)