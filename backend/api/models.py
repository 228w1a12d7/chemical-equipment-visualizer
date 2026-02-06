from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class DatasetUpload(models.Model):
    """Model to store uploaded CSV datasets and their summaries."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploads')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_equipment = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(default=0.0)
    avg_pressure = models.FloatField(default=0.0)
    avg_temperature = models.FloatField(default=0.0)
    type_distribution = models.TextField(default='{}')  # JSON string
    raw_data = models.TextField(default='[]')  # JSON string of all equipment data
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_type_distribution(self):
        """Return type distribution as dictionary."""
        return json.loads(self.type_distribution)
    
    def set_type_distribution(self, distribution):
        """Set type distribution from dictionary."""
        self.type_distribution = json.dumps(distribution)
    
    def get_raw_data(self):
        """Return raw data as list."""
        return json.loads(self.raw_data)
    
    def set_raw_data(self, data):
        """Set raw data from list."""
        self.raw_data = json.dumps(data)
    
    @classmethod
    def cleanup_old_uploads(cls, user, keep_count=5):
        """Keep only the last 'keep_count' uploads for a user."""
        uploads = cls.objects.filter(user=user).order_by('-uploaded_at')
        if uploads.count() > keep_count:
            ids_to_keep = uploads[:keep_count].values_list('id', flat=True)
            cls.objects.filter(user=user).exclude(id__in=ids_to_keep).delete()


class Equipment(models.Model):
    """Model to store individual equipment data."""
    
    dataset = models.ForeignKey(DatasetUpload, on_delete=models.CASCADE, related_name='equipment_list')
    name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField(default=0.0)
    pressure = models.FloatField(default=0.0)
    temperature = models.FloatField(default=0.0)
    recorded_at = models.DateTimeField(default=timezone.now)  # For date filtering
    
    class Meta:
        ordering = ['-recorded_at', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.equipment_type})"
