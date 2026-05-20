from django.contrib import admin
from .models import Task, UserQuery

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['text', 'user', 'priority', 'done', 'created_at']
    list_filter = ['done', 'priority']
    search_fields = ['text']

@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ['username', 'telegram_id', 'message', 'created_at']
    search_fields = ['username', 'message']