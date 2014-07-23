# -*- coding: utf-8 -*-

from fabric.api import env, task, cd, lcd, run, local, settings

from custard import VERSION

env.hosts = ['localhost']

#==============================================================================
@task
def execute_tests():
    with lcd("."):
        local("python manage.py test custard")


#==============================================================================
@task
def demo_server():
    with lcd("example"):
        local("python manage.py runserver")


#==============================================================================
@task
def update_docs():
    with lcd("docs"):
        local("make html")


#==============================================================================
@task
def create_release():
    with lcd("."):
        with settings(warn_only=True):
            local("git tag -d %s && git push origin :refs/tags/%s" % (VERSION, VERSION))
        local("git tag %s" % VERSION)
        local("git push --tags")
        local("python setup.py register -r pypi")
        local("python setup.py sdist upload -r pypi")


#==============================================================================
@task
def pypi_register(where="pypitest"):
    with lcd("."):
        local("python setup.py register -r %s" % where)


@task
def pypi_upload(where="pypitest"):
    with lcd("."):
        local("python setup.py sdist upload -r %s" % where)

