from django.contrib import admin
from .models import RoastResult

@admin.register(RoastResult)
class RoastResultAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'status', 'created_at', 'ip_address']
    list_filter = ['status', 'created_at']
    search_fields = ['task_id', 'roast_text']
    readonly_fields = ['task_id', 'status', 'created_at', 'ip_address']

