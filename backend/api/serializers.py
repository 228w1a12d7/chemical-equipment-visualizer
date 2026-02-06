from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DatasetUpload, Equipment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model."""
    
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'recorded_at']
        read_only_fields = ['id', 'recorded_at']


class EquipmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Equipment."""
    
    class Meta:
        model = Equipment
        fields = ['name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


class DatasetUploadSerializer(serializers.ModelSerializer):
    """Serializer for DatasetUpload model."""
    
    type_distribution = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DatasetUpload
        fields = [
            'id', 'filename', 'uploaded_at', 'total_equipment',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution', 'equipment_count'
        ]
    
    def get_type_distribution(self, obj):
        return obj.get_type_distribution()
    
    def get_equipment_count(self, obj):
        return obj.equipment_list.count()


class DatasetDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for DatasetUpload with equipment list."""
    
    type_distribution = serializers.SerializerMethodField()
    equipment_list = EquipmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = DatasetUpload
        fields = [
            'id', 'filename', 'uploaded_at', 'total_equipment',
            'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution', 'equipment_list'
        ]
    
    def get_type_distribution(self, obj):
        return obj.get_type_distribution()


class SummarySerializer(serializers.Serializer):
    """Serializer for data summary response."""
    
    total_equipment = serializers.IntegerField()
    avg_flowrate = serializers.FloatField()
    avg_pressure = serializers.FloatField()
    avg_temperature = serializers.FloatField()
    type_distribution = serializers.DictField()
    equipment_list = serializers.ListField()
