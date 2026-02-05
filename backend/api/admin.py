from django.contrib import admin
from .models import DatasetUpload, Equipment


@admin.register(DatasetUpload)
class DatasetUploadAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'uploaded_at', 'total_equipment']
    list_filter = ['user', 'uploaded_at']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['uploaded_at']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['name', 'equipment_type']
