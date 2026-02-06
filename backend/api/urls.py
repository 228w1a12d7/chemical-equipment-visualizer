from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/logout/', views.logout_user, name='logout'),
    path('auth/user/', views.get_current_user, name='current_user'),
    
    # Data endpoints
    path('upload/', views.upload_csv, name='upload_csv'),
    path('datasets/', views.get_upload_history, name='upload_history'),
    path('datasets/<int:dataset_id>/', views.get_dataset_summary, name='dataset_summary'),
    path('datasets/<int:dataset_id>/delete/', views.delete_dataset, name='delete_dataset'),
    path('datasets/<int:dataset_id>/pdf/', views.generate_pdf_report, name='generate_pdf'),
    path('datasets/<int:dataset_id>/csv/', views.export_csv, name='export_csv'),
    
    # Equipment CRUD endpoints
    path('datasets/<int:dataset_id>/equipment/', views.get_equipment_list, name='equipment_list'),
    path('datasets/<int:dataset_id>/equipment/add/', views.add_equipment, name='add_equipment'),
    path('datasets/<int:dataset_id>/equipment/<int:equipment_id>/', views.equipment_detail, name='equipment_detail'),
]
