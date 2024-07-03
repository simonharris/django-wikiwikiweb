============
Installation
============

.. note::

    The development team are always happy to hear suggestions for how to streamline this process.

Download
~~~~~~~~

The preferred way to source ``django-wikiwikiweb`` is via ``pip``::

    $ pip install django-wikiwikiweb

This may be a good time to add ``django-wikiwikiweb`` to your project's ``requirements.txt``.

The ``django-wikiwikiweb`` source code is also available via `the project's GitHub repository <https://github.com/simonharris/django-wikiwikiweb>`_.

Initial configuration
~~~~~~~~~~~~~~~~~~~~~

There are a few changes to make to your project's configuration files.


In settings.py
^^^^^^^^^^^^^^

1) add the app and its dependencies to ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'wikiwikiweb',
        'markdownify',
        'simple_history',
        'django_bootstrap5',
    ]


2) enable the ``django-simple-history`` middleware by adding the following entry to ``MIDDLEWARE``::

    MIDDLEWARE = [
        ...
        'simple_history.middleware.HistoryRequestMiddleware',
    ]


3) enable the ``django-wikiwikweb`` context processor by adding the following to entry to ``TEMPLATES``::

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'context_processors': [
                   ...
                   'wikiwikiweb.context_processors.site_wide_context',
                ],
            },
        },
    ]


In urls.py
^^^^^^^^^^

4) Include the ``django-wikiwikiweb`` URL routes file in your ``urlpatterns``::

    urlpatterns = [
        # To run under a path:
        path('wiki/', include('wikiwikiweb.urls')),
        ...
        # OR it will also run just fine as a standalone site:
        #path('', include('wikiwikiweb.urls')),
        ...
        # Don't forget Django's own routes for login/logout
        path('accounts/', include('django.contrib.auth.urls')),
    ]



Database migrations
^^^^^^^^^^^^^^^^^^^

Finally, apply the database migrations to create the tables needed by ``django-wikiwikiweb``:


.. code-block:: console

    $ python manage.py migrate wikiwikiweb


You should be good to go. Upon starting the Django server, you should now have an empty wiki under ``/wiki/``, or wherever you chose for it to live. A WikiWikiWeb section should now be available under the Django admin site.

Therefore, there will soon be a link to a Quickstart guide for Wiki admins here.

Optional settings
^^^^^^^^^^^^^^^^^


There are a small number of optional settings to consider.

These are to follow...




