django-deploy-template
========================
Django 的几种部署方式的模版。

主要提供了三种方式

* Apache + mod_wsgi
* Apache + mod_fcgid + mod_rewrite
* Nginx + fcgi 

部署用用到的文件（fabfile.py,虚拟主机文件,相关的脚本等) 放在 `deploy/<deploy_method>` 目录下面。

示例的Django 工程为 django_hello_world


