from django.contrib import admin
from head_admin.models import HeadAdmin

# Register your models here.

class HeadAdminAdmin(admin.ModelAdmin):
    list_display = ('h_name','h_email','h_id')
    
admin.site.register(HeadAdmin,HeadAdminAdmin)