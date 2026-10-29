"""
WSGI config for aether_core project.

WSGI = Web Server Gateway Interface. This is the standard way Python web
applications communicate with web servers. When you run the Django server,
this file is the "bridge" between the server software and our Django code.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aether_core.settings')

application = get_wsgi_application()
