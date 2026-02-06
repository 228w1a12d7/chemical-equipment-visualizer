"""
URL configuration for chemical_visualizer project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def home(request):
    """API welcome page with beautiful HTML landing page."""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chemical Equipment Visualizer API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            max-width: 800px;
            width: 100%;
            padding: 40px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 28px;
            color: #1e293b;
            margin-bottom: 10px;
        }
        .header .icon { font-size: 48px; margin-bottom: 15px; }
        .status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #ecfdf5;
            color: #059669;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
        }
        .status::before {
            content: '';
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .section {
            margin-top: 30px;
        }
        .section h2 {
            font-size: 18px;
            color: #4f46e5;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .endpoints {
            background: #f8fafc;
            border-radius: 12px;
            padding: 20px;
        }
        .endpoint {
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        .endpoint:last-child { border-bottom: none; }
        .method {
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            min-width: 70px;
            text-align: center;
            margin-right: 15px;
        }
        .method.get { background: #dbeafe; color: #1d4ed8; }
        .method.post { background: #dcfce7; color: #16a34a; }
        .method.delete { background: #fee2e2; color: #dc2626; }
        .path {
            font-family: 'Monaco', 'Consolas', monospace;
            color: #475569;
            font-size: 14px;
        }
        .links {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        .link {
            flex: 1;
            min-width: 200px;
            padding: 20px;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            text-align: center;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .link:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }
        .link.secondary {
            background: linear-gradient(135deg, #10b981, #059669);
        }
        .link .icon { font-size: 24px; display: block; margin-bottom: 8px; }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #94a3b8;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="icon">🔬</div>
            <h1>Chemical Equipment Parameter Visualizer</h1>
            <p style="color: #64748b; margin-bottom: 15px;">REST API Backend Server</p>
            <span class="status">API Running</span>
        </div>

        <div class="section">
            <h2>🔐 Authentication Endpoints</h2>
            <div class="endpoints">
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/api/auth/register/</span>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/api/auth/login/</span>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/api/auth/logout/</span>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/api/auth/user/</span>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Data Endpoints</h2>
            <div class="endpoints">
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="path">/api/upload/</span>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/api/datasets/</span>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/api/datasets/{id}/</span>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="path">/api/datasets/{id}/pdf/</span>
                </div>
                <div class="endpoint">
                    <span class="method delete">DELETE</span>
                    <span class="path">/api/datasets/{id}/delete/</span>
                </div>
            </div>
        </div>

        <div class="links">
            <a href="http://localhost:3000" class="link">
                <span class="icon">🌐</span>
                Web Application
            </a>
            <a href="/admin/" class="link secondary">
                <span class="icon">⚙️</span>
                Admin Panel
            </a>
        </div>

        <div class="footer">
            <p>Version 1.0.0 | Django REST Framework</p>
        </div>
    </div>
</body>
</html>'''
    return HttpResponse(html, content_type='text/html')


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
