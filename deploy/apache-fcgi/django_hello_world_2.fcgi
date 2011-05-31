#!/opt/app/django_hello_world_2/bin/python
import sys, os

PROJECT_NAME = 'django_hello_world_2'
DJANGO_PROJECT_NAME = 'django_hello_world'

# Add a custom Python path.
sys.path.insert(0, "/opt/app/%s/releases/current/" %PROJECT_NAME)
sys.path.insert(0, "/opt/app/%s/releases/current/%s" %(PROJECT_NAME,DJANGO_PROJECT_NAME))

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "%s.settings" %DJANGO_PROJECT_NAME

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
