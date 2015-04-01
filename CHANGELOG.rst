Changelog
=========

Only important changes are mentioned below.


v0.9 (2015-03-12)
-----------------

* Added ability to pass "value" in CustomValuesModel.objects.create
* Fixed https://github.com/kunitoki/django-custard/pull/2
* More tests and fixes


v0.8 (2014-10-08)
-----------------

* Fixed https://github.com/kunitoki/django-custard/issues/1
* More tests
* More coverage


v0.7 (2014-07-29)
-----------------

* Moved away from the static custard.models.custom class in favour of custard.builder
* Enable search of custom fields in admin without hacks
* Simplified a bit how to determine the classes in the builder
* Updated tests and example to the new builder methods


v0.6 (2014-07-27)
-----------------

* Added support for python 2.6/2.7/3.2 and django 1.5/1.6
* Added test cases for forms and widgets
* Improved settings class to be cached at runtime while being able to work with override_settings in tests
* Fixed documentation links and sections not showing up


v0.5 (2014-07-23)
-----------------

* Removed useless custom Exception classes not used anymore
* Added model mixin creation class for holding additional helper functions
* Fixed broken links in docs
* Added manager subclass to docs
* Added admin to docs


v0.4 (2014-07-23)
-----------------

* Moved generation of FormField from model to Form
* Improved documentation


v0.3 (2014-07-22)
-----------------

* Improved documentation


v0.2 (2014-07-20)
-----------------

* Avoid using a global registry for registered apps in favour of a setting variable
* Improved documentation


v0.1 (2014-07-18)
-----------------

* First stable version released
