"""
"""
from __future__ import with_statement
from fabric.api import env, run,require, sudo, run, put, local, settings, cd
from fabric.contrib.files import upload_template, exists

env.project_name = 'django_hello_world_3'
env.dj_project_name = 'django_hello_world'
# environments

def conf():
    "Use the local virtual server"
    env.hosts = ['127.0.0.1']
    env.path = '/opt/app/%s' %env.project_name
    env.user = 'ftao'
    env.group = 'ftao'
    env.key_filename = '/home/ftao/.ssh/deploy_key'
    env.deploy_path = "deploy/nginx-fcgi/"

# tasks

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories
    """
    require('hosts', provided_by=[conf])
    require('path')
    
    sudo('aptitude install -y python-setuptools')
    sudo('aptitude install -y nginx')
    sudo('aptitude install -y daemon')

    sudo('easy_install pip')
    sudo('pip install virtualenv')
    #sudo('aptitude install -y python-mysqldb')
    sudo('mkdir -p %(path)s; cd %(path)s; virtualenv .;chown -R %(group)s:%(user)s .;' %env)
    with settings(warn_only=True):
        run('cd %(path)s; mkdir releases;mkdir packages;mkdir run;mkdir log; mkdir share;chmod 777 -R share;' %env)
        run('cd %(path)s; chown -R www-data:www-data run; chown -R www-data:www-data log;' %env)

def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    require('hosts', provided_by=[conf])
    require('path')

    import time
    env.release = time.strftime('%Y%m%d%H%M%S')

    #upload_tar_from_hg()
    upload_tar_from_git()
    install_requirements()
    #install_product_settings()

    install_site()
    install_daemon()
    symlink_current_release()
    #migrate()
    restart_daemon()
    restart_webserver()

def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', provided_by=[conf])
    require('path')
    env.version = version
    with cd('%(path)s/releases' %env):
        run('rm previous; mv current previous;' %env)
        run('ln -s %(version)s current' %env)
    restart_webserver()

def retry(release):
    env.release = release
    
def rollback():
    """
    Limited rollback capability. Simple loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[conf])
    require('path')
    with cd('%(path)s' %env):
        run('mv releases/current releases/_previous;')
        run('mv releases/previous releases/current;')
        run('mv releases/_previous releases/previous;')
    restart_webserver()
    
# Helpers. These are called by other functions rather than directly

def upload_tar_from_hg():
    require('release', provided_by=[deploy, retry])
    "Create an archive from the current Git master branch and upload it"
    local("hg archive %(release)s.tar.gz" %env)
    run('mkdir %(path)s/releases/%(release)s' %env)
    put('%(release)s.tar.gz' %env, '%(path)s/packages/' %env)
    run('cd %(path)s/releases/%(release)s && tar --strip-components=1 -xzf ../../packages/%(release)s.tar.gz ' %env)
    local('rm %(release)s.tar.gz' %env)

def upload_tar_from_git():
    require('release', provided_by=[deploy, retry])
    "Create an archive from the current Git master branch and upload it"
    local("git archive --format=tar master | gzip > %(release)s.tar.gz" %env)
    run('mkdir %(path)s/releases/%(release)s' %env)
    put('%(release)s.tar.gz' %env, '%(path)s/packages/' %env)
    run('cd %(path)s/releases/%(release)s && tar -xzf ../../packages/%(release)s.tar.gz ' %env)
    local('rm %(release)s.tar.gz' %env)

def install_site():
    "Add the virtualhost file to apache"
    require('release', provided_by=[deploy])
    sudo('cd %(path)s/releases/%(release)s; cp %(deploy_path)s%(project_name)s /etc/nginx/sites-available/' %env)
    sudo('cd /etc/nginx/sites-enabled/; ln -sf ../sites-available/%(project_name)s' %env) 

def install_daemon():
    require('release', provided_by=[deploy])
    sudo('cd %(path)s/releases/%(release)s; cp %(deploy_path)s%(project_name)s_daemon /etc/init.d/' %env)
    sudo('update-rc.d %(project_name)s_daemon defaults' %env)

def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, retry])
    run('cd %(path)s; pip install -E . -r ./releases/%(release)s/%(deploy_path)srequirements.txt' %env)

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, retry])
    with settings(warn_only=True):
        run('cd %(path)s; rm releases/previous; mv releases/current releases/previous;' %env)
    run('cd %(path)s/releases; ln -s %(release)s current' %env)

def migrate():
    "Update the database"
    require('path')
    with cd('%(path)s/releases/current/%(dj_project_name)s/' %env):
        run('%(path)s/bin/python manage.py syncdb --noinput' %env)
        run('%(path)s/bin/python manage.py migrate --noinput' %env)

def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/nginx restart')

def restart_daemon():
    require('project_name')
    sudo('/etc/init.d/%(project_name)s_daemon stop' %env)
    sudo('/etc/init.d/%(project_name)s_daemon start' %env)
