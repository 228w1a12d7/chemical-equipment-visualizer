"""
WSGI config for chemical_visualizer project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical_visualizer.settings')

application = get_wsgi_application()
