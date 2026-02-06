"""
URL configuration for chemical_visualizer project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def home(request):
    """API welcome page with endpoint documentation."""
    return JsonResponse({
        "name": "Chemical Equipment Parameter Visualizer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": {
                "register": "POST /api/auth/register/",
                "login": "POST /api/auth/login/",
                "logout": "POST /api/auth/logout/",
                "user": "GET /api/auth/user/"
            },
            "data": {
                "upload": "POST /api/upload/",
                "datasets": "GET /api/datasets/",
                "dataset_detail": "GET /api/datasets/{id}/",
                "dataset_pdf": "GET /api/datasets/{id}/pdf/",
                "delete_dataset": "DELETE /api/datasets/{id}/delete/"
            }
        },
        "documentation": "Use the endpoints above to interact with the API",
        "admin": "/admin/"
    })


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
