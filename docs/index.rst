.. image:: ../custard-logo.png
   :alt: Django Custard
   :target: https://github.com/kunitoki/django-custard

==================================
Django runtime typed custom fields
==================================

Django Custard is a small reusable unobtrusive `Django <http://www.djangoproject.com>`_
app that implements runtime custom fields that can be attached to any model on the
fly: it's possible to create fields and set values for them from the code or
manage them through the admin site, with the ability to display them even outside
of the admin.

.. |travis| image:: https://travis-ci.org/kunitoki/django-custard.png?branch=master
   :alt: Build Status - master branch
   :target: https://travis-ci.org/kunitoki/django-custard

.. |coveralls| image:: https://coveralls.io/repos/kunitoki/django-custard/badge.png?branch=master
   :alt: Source code coverage - master branch
   :target: https://coveralls.io/r/kunitoki/django-custard

.. |pythonversions| image:: https://pypip.in/py_versions/django-custard/badge.png
    :target: https://pypi.python.org/pypi/django-custard/
    :alt: Supported Python versions

.. |pypi| image:: https://pypip.in/v/django-custard/badge.png
   :alt: Pypi latest version
   :target: https://pypi.python.org/pypi/django-custard/

.. |downloads| image:: https://pypip.in/d/django-custard/badge.png
   :alt: Pypi downloads
   :target: https://pypi.python.org/pypi/django-custard/

.. |license| image:: https://pypip.in/license/django-custard/badge.png
    :target: https://pypi.python.org/pypi/django-custard/
    :alt: License

|pypi| |travis| |coveralls| |downloads| |pythonversions| |license|


Resources
=========

* Home page: https://github.com/kunitoki/django-custard
* Documentation: http://django-custard.readthedocs.org
* Pypi: https://pypi.python.org/pypi/django-custard
* Example app on Github: https://github.com/kunitoki/django-custard/example
* Changelog: `Changelog.rst <https://github.com/kunitoki/django-custard/blob/master/CHANGELOG.rst>`_
* License: `The MIT License (MIT) <http://opensource.org/licenses/MIT>`_
* Supports: Django 1.5, 1.6 - Python 2.6, 2.7, 3.2


Installation
============

1. You can get Django Custard by using pip::

    pip install django-custard

2. You will need to add the ``'custard'`` application to the ``INSTALLED_APPS`` setting of your Django project ``settings.py`` file.::

    INSTALLED_APPS = (
        ...

        'custard',
    )

3. In a ``models.py`` file in your app you should just add the 2 models responsible of holding the custom fields type and values.::

    from custard.models import custom

    ...

    class CustomFieldsModel(custom.create_fields()):
        pass

    class CustomValuesModel(custom.create_values(CustomFieldsModel)):
        pass


Customization
=============

Configuration
-------------

Customize Django Custard with some ``CUSTOM_*`` configuration variables in a
Django project ``settings.py`` file.

.. toctree::
   :maxdepth: 3

   configuration


Models
------

How to work with Django Custard models and helper classes.

.. toctree::
   :maxdepth: 3

   models


Admin
-----

Process of integrating Django Custard in admin.

.. toctree::
   :maxdepth: 3

   admin


Support
=======

* Github: Use `django-custard github issues <https://github.com/kunitoki/django-custard/issues>`_, if you have any problems using Django Custard.
