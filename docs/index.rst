.. include:: ../README.rst


Getting started
===============

1. You can get Django Custard by using pip::

    pip install django-custard

2. You will need to add the ``'custard'`` application to the ``INSTALLED_APPS`` setting of your Django project ``settings.py`` file.::

    INSTALLED_APPS = (
        ...

        'custard',
    )

3. In a ``models.py`` file in your app you should just add the 2 models responsible of holding the custom fields type and values.::

    from custard.builder import CustomFieldsBuilder

    builder = CustomFieldsBuilder('myapp.CustomFieldsModel', 'myapp.CustomValuesModel')

    ...

    class CustomFieldsModel(builder.create_fields()):
        pass

    class CustomValuesModel(builder.create_values()):
        pass

4. Then sync your database with::

    python manager.py syncdb


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


.. include:: ../CHANGELOG.rst
