"""
ASGI config for ame_control project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ame_control.settings')

application = get_asgi_application()
