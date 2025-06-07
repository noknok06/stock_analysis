# notebooks/admin.py
from django.contrib import admin
from .models import Notebook, Entry

@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'stock_code', 'current_price', 'target_price', 'entry_count', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'is_public']
    search_fields = ['title', 'company_name', 'stock_code']
    readonly_fields = ['created_at', 'updated_at', 'entry_count']

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'notebook', 'entry_type', 'created_at']
    list_filter = ['entry_type', 'created_at']
    search_fields = ['title', 'content']