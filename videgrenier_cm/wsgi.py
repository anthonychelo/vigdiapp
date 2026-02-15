import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videgrenier_cm.settings')
application = get_wsgi_application()
