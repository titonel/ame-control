"""
WSGI config for ame_control project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ame_control.settings')

application = get_wsgi_application()
