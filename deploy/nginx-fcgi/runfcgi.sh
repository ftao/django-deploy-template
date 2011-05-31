#!/bin/sh
EGG_CACHE_DIR="/opt/app/django_hello_world_3/share/.python-eggs"
export PYTHON_EGG_CACHE=$EGG_CACHE_DIR
/opt/app/django_hello_world_3/bin/python /opt/app/django_hello_world_3/releases/current/django_hello_world/manage.py runfcgi daemonize=false socket=/opt/app/django_hello_world_3/run/django_hello_world_3.sock pidfile=/opt/app/django_hello_world_3/run/django_hello_world_3.pid
