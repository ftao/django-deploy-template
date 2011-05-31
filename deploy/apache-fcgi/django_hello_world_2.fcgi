#!/opt/app/django_hello_world_2/bin/python
import sys, os

PROJECT_NAME = 'django_hello_world_2'
DJANGO_PROJECT_NAME = 'django_hello_world'

VE_PREFIX = '/opt/app/'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(VE_PREFIX, PROJECT_NAME, 'share/.python-eggs')

# Add a custom Python path.
sys.path.insert(0, os.path.join(VE_PREFIX, PROJECT_NAME, "releases/current"))

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "%s.settings" %DJANGO_PROJECT_NAME

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
