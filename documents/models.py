from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Document(models.Model):
    """
    Stores uploaded medical documents (PDFs, images, etc.)
    Each document belongs to a user (doctor/admin)
    """
    # Relationship: Each document belongs to one user
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='documents'
    )
    
    # File storage
    file = models.FileField(
        upload_to='documents/%Y/%m/%d/',  # Organizes by date: documents/2025/11/20/
        help_text='Upload medical document (PDF, JPG, PNG)'
    )
    
    # Document metadata
    original_filename = models.CharField(max_length=255, blank=True)
    file_type = models.CharField(max_length=50, blank=True)  # 'pdf', 'jpg', etc.
    file_size = models.IntegerField(default=0, help_text='File size in bytes')
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'Pending Processing'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Extracted content (raw text from document)
    extracted_text = models.TextField(blank=True, help_text='Raw text extracted from document')
    
    class Meta:
        ordering = ['-uploaded_at']  # Newest first
        verbose_name = 'Medical Document'
        verbose_name_plural = 'Medical Documents'
    
    def __str__(self):
        return f"{self.original_filename} - {self.user.username} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Auto-populate filename and type on save"""
        if self.file and not self.original_filename:
            self.original_filename = self.file.name.split('/')[-1]
            self.file_type = self.original_filename.split('.')[-1].lower()
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class Summary(models.Model):
    """
    Stores AI-generated summaries for each document
    One document can have multiple summary versions
    """
    # Relationship: Each summary belongs to one document
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='summaries'
    )
    
    # AI-generated content
    summary_text = models.TextField(help_text='AI-generated medical summary')
    
    # Extracted entities (JSON format for flexibility)
    extracted_entities = models.JSONField(
        default=dict,
        blank=True,
        help_text='Medical entities: symptoms, diagnosis, medications, etc.'
    )
    
    # Summary metadata
    model_used = models.CharField(
        max_length=100, 
        default='gemini-pro',
        help_text='AI model used for generation'
    )
    
    confidence_score = models.FloatField(
        default=0.0,
        help_text='AI confidence score (0-1)'
    )
    
    # User interaction
    is_edited = models.BooleanField(default=False)
    edited_text = models.TextField(blank=True, help_text='User-edited version')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Summary'
        verbose_name_plural = 'AI Summaries'
    
    def __str__(self):
        return f"Summary for {self.document.original_filename}"
    
    def get_final_text(self):
        """Returns edited text if available, otherwise original summary"""
        return self.edited_text if self.is_edited else self.summary_text
