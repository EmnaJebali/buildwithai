"""
ASGI config for tetris_therapist project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tetris_therapist.settings')

application = get_asgi_application()

