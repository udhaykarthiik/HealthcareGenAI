from django.contrib import admin
from .models import Document, Summary

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for Document model
    Provides search, filters, and detailed view
    """
    list_display = [
        'original_filename', 
        'user', 
        'file_type', 
        'status', 
        'uploaded_at',
        'file_size_display'
    ]
    list_filter = ['status', 'file_type', 'uploaded_at']
    search_fields = ['original_filename', 'user__username', 'extracted_text']
    readonly_fields = ['uploaded_at', 'processed_at', 'file_size']
    
    fieldsets = (
        ('Document Info', {
            'fields': ('user', 'file', 'original_filename', 'file_type', 'file_size')
        }),
        ('Processing', {
            'fields': ('status', 'uploaded_at', 'processed_at', 'extracted_text')
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        size_kb = obj.file_size / 1024
        if size_kb < 1024:
            return f"{size_kb:.1f} KB"
        return f"{size_kb/1024:.1f} MB"
    file_size_display.short_description = 'File Size'


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    """
    Admin interface for Summary model
    """
    list_display = [
        'document', 
        'model_used', 
        'confidence_score',
        'is_edited',
        'created_at'
    ]
    list_filter = ['model_used', 'is_edited', 'created_at']
    search_fields = ['summary_text', 'edited_text', 'document__original_filename']
    readonly_fields = ['created_at', 'edited_at']
    
    fieldsets = (
        ('Summary Info', {
            'fields': ('document', 'summary_text', 'extracted_entities')
        }),
        ('AI Metadata', {
            'fields': ('model_used', 'confidence_score')
        }),
        ('User Edits', {
            'fields': ('is_edited', 'edited_text', 'created_at', 'edited_at')
        }),
    )
