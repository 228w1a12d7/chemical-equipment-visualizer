import io
import pandas as pd
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

from .models import DatasetUpload, Equipment
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    DatasetUploadSerializer, DatasetDetailSerializer,
    EquipmentSerializer, SummarySerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Authenticate user and return token."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user exists first
    from django.contrib.auth.models import User
    user_exists = User.objects.filter(username=username).exists()
    
    if not user_exists:
        return Response(
            {'error': 'User not found. Please sign up first to create an account.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'token': token.key
        })
    return Response(
        {'error': 'Incorrect password. Please try again.'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """Logout user by deleting their token."""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Get current authenticated user info."""
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """
    Upload and process a CSV file containing equipment data.
    Expected columns: Equipment Name, Type, Flowrate, Pressure, Temperature
    """
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    csv_file = request.FILES['file']
    
    if not csv_file.name.endswith('.csv'):
        return Response(
            {'error': 'File must be a CSV'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Read CSV with pandas
        df = pd.read_csv(csv_file)
        
        # Normalize column names (strip whitespace, handle variations)
        df.columns = df.columns.str.strip()
        
        # Map possible column name variations
        column_mapping = {
            'Equipment Name': ['Equipment Name', 'equipment_name', 'Name', 'name'],
            'Type': ['Type', 'type', 'Equipment Type', 'equipment_type'],
            'Flowrate': ['Flowrate', 'flowrate', 'Flow Rate', 'flow_rate'],
            'Pressure': ['Pressure', 'pressure'],
            'Temperature': ['Temperature', 'temperature', 'Temp', 'temp']
        }
        
        # Find actual column names
        actual_columns = {}
        for standard_name, variations in column_mapping.items():
            for variation in variations:
                if variation in df.columns:
                    actual_columns[standard_name] = variation
                    break
        
        # Validate required columns exist
        required = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing = [col for col in required if col not in actual_columns]
        
        if missing:
            return Response(
                {'error': f'Missing required columns: {missing}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rename columns to standard names
        rename_map = {v: k for k, v in actual_columns.items()}
        df = df.rename(columns=rename_map)
        
        # Calculate statistics
        total_equipment = len(df)
        avg_flowrate = round(df['Flowrate'].mean(), 2)
        avg_pressure = round(df['Pressure'].mean(), 2)
        avg_temperature = round(df['Temperature'].mean(), 2)
        
        # Calculate type distribution
        type_distribution = df['Type'].value_counts().to_dict()
        
        # Create dataset upload record
        dataset = DatasetUpload.objects.create(
            user=request.user,
            filename=csv_file.name,
            total_equipment=total_equipment,
            avg_flowrate=avg_flowrate,
            avg_pressure=avg_pressure,
            avg_temperature=avg_temperature
        )
        dataset.set_type_distribution(type_distribution)
        
        # Store raw data as JSON
        raw_data = df.to_dict('records')
        dataset.set_raw_data(raw_data)
        dataset.save()
        
        # Create Equipment records
        equipment_objects = []
        for _, row in df.iterrows():
            equipment_objects.append(Equipment(
                dataset=dataset,
                name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=row['Flowrate'],
                pressure=row['Pressure'],
                temperature=row['Temperature']
            ))
        Equipment.objects.bulk_create(equipment_objects)
        
        # Cleanup old uploads (keep only last 5)
        DatasetUpload.cleanup_old_uploads(request.user, keep_count=5)
        
        # Prepare response
        equipment_list = [{
            'id': idx + 1,
            'name': row['Equipment Name'],
            'type': row['Type'],
            'flowrate': row['Flowrate'],
            'pressure': row['Pressure'],
            'temperature': row['Temperature']
        } for idx, row in df.iterrows()]
        
        return Response({
            'message': 'File uploaded successfully',
            'dataset_id': dataset.id,
            'summary': {
                'total_equipment': total_equipment,
                'avg_flowrate': avg_flowrate,
                'avg_pressure': avg_pressure,
                'avg_temperature': avg_temperature,
                'type_distribution': type_distribution
            },
            'equipment_list': equipment_list
        }, status=status.HTTP_201_CREATED)
        
    except pd.errors.EmptyDataError:
        return Response(
            {'error': 'CSV file is empty'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Error processing file: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dataset_summary(request, dataset_id):
    """Get summary for a specific dataset."""
    try:
        dataset = DatasetUpload.objects.get(id=dataset_id, user=request.user)
        
        equipment_list = [{
            'id': eq.id,
            'name': eq.name,
            'type': eq.equipment_type,
            'flowrate': eq.flowrate,
            'pressure': eq.pressure,
            'temperature': eq.temperature
        } for eq in dataset.equipment_list.all()]
        
        return Response({
            'dataset_id': dataset.id,
            'filename': dataset.filename,
            'uploaded_at': dataset.uploaded_at,
            'summary': {
                'total_equipment': dataset.total_equipment,
                'avg_flowrate': dataset.avg_flowrate,
                'avg_pressure': dataset.avg_pressure,
                'avg_temperature': dataset.avg_temperature,
                'type_distribution': dataset.get_type_distribution()
            },
            'equipment_list': equipment_list
        })
    except DatasetUpload.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_upload_history(request):
    """Get the last 5 uploaded datasets for the current user."""
    datasets = DatasetUpload.objects.filter(user=request.user)[:5]
    serializer = DatasetUploadSerializer(datasets, many=True)
    return Response({
        'count': datasets.count(),
        'datasets': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_dataset(request, dataset_id):
    """Delete a specific dataset."""
    try:
        dataset = DatasetUpload.objects.get(id=dataset_id, user=request.user)
        dataset.delete()
        return Response({'message': 'Dataset deleted successfully'})
    except DatasetUpload.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request, dataset_id):
    """Generate a PDF report for a specific dataset."""
    try:
        dataset = DatasetUpload.objects.get(id=dataset_id, user=request.user)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a5276'),
            alignment=1  # Center
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2874a6')
        )
        normal_style = styles['Normal']
        
        elements = []
        
        # Title
        elements.append(Paragraph("Chemical Equipment Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Dataset info
        elements.append(Paragraph(f"<b>Filename:</b> {dataset.filename}", normal_style))
        elements.append(Paragraph(f"<b>Generated:</b> {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Paragraph(f"<b>User:</b> {request.user.username}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Summary section
        elements.append(Paragraph("Summary Statistics", heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Equipment', str(dataset.total_equipment)],
            ['Average Flowrate', f"{dataset.avg_flowrate:.2f}"],
            ['Average Pressure', f"{dataset.avg_pressure:.2f}"],
            ['Average Temperature', f"{dataset.avg_temperature:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 150])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2874a6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eaf2f8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#aed6f1')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Type distribution section
        elements.append(Paragraph("Equipment Type Distribution", heading_style))
        
        type_dist = dataset.get_type_distribution()
        type_data = [['Equipment Type', 'Count']]
        for eq_type, count in type_dist.items():
            type_data.append([eq_type, str(count)])
        
        type_table = Table(type_data, colWidths=[250, 100])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e8449')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e9f7ef')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a9dfbf')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(type_table)
        elements.append(Spacer(1, 30))
        
        # Equipment list section
        elements.append(Paragraph("Equipment Details", heading_style))
        
        equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        for eq in dataset.equipment_list.all()[:50]:  # Limit to 50 for PDF
            equipment_data.append([
                eq.name,
                eq.equipment_type,
                f"{eq.flowrate:.1f}",
                f"{eq.pressure:.1f}",
                f"{eq.temperature:.1f}"
            ])
        
        equipment_table = Table(equipment_data, colWidths=[100, 100, 70, 70, 80])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c3483')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5eef8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d7bde2')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ]))
        elements.append(equipment_table)
        
        # Build PDF
        doc.build(elements)
        
        # Create response
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset_id}.pdf"'
        
        return response
        
    except DatasetUpload.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error generating PDF: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
