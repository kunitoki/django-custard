.. image:: ../custard-logo.png
   :alt: Django Custard
   :target: https://github.com/kunitoki/django-custard

==========================================
Django runtime customizable generic fields
==========================================

Django Custard is a small reusable `Django <http://www.djangoproject.com>`_ app
that implements runtime customizable fields that can be attached to any model
on the fly: add fields from the admin interface and display them in any model,
even outside of the admin.

.. |travis| image:: https://travis-ci.org/kunitoki/django-custard.png?branch=master
   :alt: Build Status - master branch
   :target: https://travis-ci.org/kunitoki/django-custard

.. |coveralls| image:: https://coveralls.io/repos/kunitoki/django-custard/badge.png
   :alt: Source code coverage - master branch
   :target: https://coveralls.io/r/kunitoki/django-custard

.. |pypi| image:: https://pypip.in/v/django-custard/badge.png
   :alt: Pypi latest version
   :target: https://pypi.python.org/pypi/django-custard/

.. |downloads| image:: https://pypip.in/d/django-custard/badge.png
   :alt: Pypi downloads
   :target: https://pypi.python.org/pypi/django-custard/

|travis| |coveralls| |pypi| |downloads|


Licence
-------

* Django Custard is licensed under `The MIT License (MIT) <http://opensource.org/licenses/MIT>`_ license.


Resources
---------

* Home page: https://github.com/kunitoki/django-custard
* Licence: https://github.com/kunitoki/django-custard/blob/master/LICENSE.txt
* Documentation: http://django-custard.readthedocs.org/en/latest
* Example app on Github: https://github.com/kunitoki/django-custard/example
* Changelog: `Changelog.rst <https://github.com/kunitoki/django-custard/blob/develop/CHANGELOG.rst>`_
* Supports: Django 1.6 - Python 2.7


Installation
============

1. You can get Django Custard by using pip or easy_install::

    pip install django-custard
    # or
    easy_install django-custard

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

You can customize Django Custard with some ``CUSTOM_*`` configuration variables
to your Django project ``settings.py`` file.

.. toctree::
   :maxdepth: 3

   configuration


Models
------

.. toctree::
   :maxdepth: 3

   models


Forms
-----

Form tabs help you organize form fieldsets and inlines into tabs.

.. toctree::
   :maxdepth: 1

   forms


Admin integration
-----------------

There are handy widgets included in Django Suit.

.. toctree::
   :maxdepth: 3

   admin



Support
=======

* Github: Use `django-custard github issues <https://github.com/kunitoki/django-custard/issues>`_, if you have any problems using Django Custard.
