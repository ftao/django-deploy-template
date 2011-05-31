"""
"""
# globals

from __future__ import with_statement
from fabric.api import env, run,require, sudo, run, put, local, settings, cd
from fabric.contrib.files import upload_template, exists

env.project_name = 'django_hello_world'
# environments

def conf():
    "Use the local virtual server"
    env.hosts = ['127.0.0.1']
    env.path = '/opt/app/%s' %env.project_name
    env.user = 'ftao'
    env.group = 'ftao'
    env.key_filename = '/home/ftao/.ssh/deploy_key'
    env.virtualhost_path = "deploy/modwsgi/"

# tasks

def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories
    """
    require('hosts', provided_by=[conf])
    require('path')
    
    sudo('aptitude install -y python-setuptools')
    sudo('aptitude install -y apache2')
    sudo('aptitude install -y libapache2-mod-rewrite')
    sudo('aptitude install -y libapache2-mod-wsgi')
    #sudo('aptitude install -y libapache2-mod-fcgid')
    sudo('a2enmod rewrite')
    sudo('a2enmod wsgi')

    sudo('easy_install pip')
    sudo('pip install virtualenv')
    #sudo('aptitude install -y python-mysqldb')
    sudo('mkdir -p %(path)s; cd %(path)s; virtualenv .;chown -R %(group)s:%(user)s .;' %env)
    with settings(warn_only=True):
        run('cd %(path)s; mkdir releases;mkdir packages;mkdir share;mkdir -p share/.python-eggs; chmod 777 -R share;' %env)
    #deploy()


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
    symlink_current_release()
    #migrate()
    #install_cron_job()
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
    sudo('cd %(path)s/releases/%(release)s; cp %(virtualhost_path)s%(project_name)s /etc/apache2/sites-available/' %env)
    sudo('cd /etc/apache2/sites-available/; a2ensite %(project_name)s' %env) 

def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, retry])
    run('cd %(path)s; pip install -E . -r ./releases/%(release)s/requirements.txt' %env)

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, retry])
    with settings(warn_only=True):
        run('cd %(path)s; rm releases/previous; mv releases/current releases/previous;' %env)
    run('cd %(path)s/releases; ln -s %(release)s current' %env)

def migrate():
    "Update the database"
    require('path')
    with cd('%(path)s/releases/current/%(project_name)s/' %env):
        run('%(path)s/bin/python manage.py syncdb --noinput' %env)
        run('%(path)s/bin/python manage.py migrate --noinput' %env)

def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/apache2 restart')
