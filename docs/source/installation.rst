============
Installation
============

.. note::

   This project is under active development. It is not yet available under ``pip``. The source code repository is `available on GitHub <https://github.com/simonharris/django-wikiwikiweb>`_.


The preferred way to install ``django-wikiwikiweb`` will be ``pip``::

    $ pip install django-wikiwikiweb


In your project, you should add ``django-wikiwikiweb`` to your ``requirements.txt``.

Add the app to INSTALLED_APPS in your ``settings.py``:

   ``'django_wikiwikiweb',``

..or is it?

    ``'wikiwikiweb',``

Further settings will be documented here in due course.


The dependencies are currently:

* Django 5 - ``pip install Django``
* django-markdownify - ``pip install django-markdownify``
* django-simple-history - ``pip install django-simple-history``
* django-bootstrap5 - ``pip install django-bootstrap5``
