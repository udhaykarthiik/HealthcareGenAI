from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class Document(models.Model):
    """
    Model to store uploaded medical documents and AI processing results
    """
    DOCUMENT_TYPES = [
        ('general', 'General Medical Document'),
        ('discharge', 'Discharge Summary'),
        ('referral', 'Referral Letter'),
        ('insurance', 'Insurance Authorization'),
        ('lab_report', 'Lab Report'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # User who uploaded the document
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    
    # File information
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)  # pdf, jpg, png, etc.
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='general')
    
    # Document content
    extracted_text = models.TextField(blank=True, null=True)
    entities = models.JSONField(default=dict, blank=True)  # Store extracted entities as JSON
    ai_summary = models.TextField(blank=True, null=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.user.username} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-set processed_at when status changes to completed
        if self.status == 'completed' and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)
    
    def get_entities_dict(self):
        """Return entities as a dictionary"""
        if isinstance(self.entities, dict):
            return self.entities
        try:
            return json.loads(self.entities) if self.entities else {}
        except:
            return {}