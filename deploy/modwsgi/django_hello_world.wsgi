import sys
import site
import os

#change this to your project name 
PROJECT_NAME = 'django_hello_world'
VE_PREFIX = '/opt/app/'

vepath = os.path.join(VE_PREFIX, PROJECT_NAME, 'lib/python2.5/site-packages')
release_path = os.path.join(VE_PREFIX, PROJECT_NAME, 'releases/current')

prev_sys_path = list(sys.path)
# add the site-packages of our virtualenv as a site dir
site.addsitedir(vepath)
# add the app's directory to the PYTHONPATH
sys.path.append(release_path)

# reorder sys.path so new directories from the addsitedir show up first
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

from django.core.handlers.wsgi import WSGIHandler
os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' %PROJECT_NAME
application = WSGIHandler()
