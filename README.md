# Django Cravensworth

![docs build status](https://app.readthedocs.org/projects/django-cravensworth/badge/?version=latest)

django-cravensworth is a Django app for experimentation.

## Quick start

Install the Cravensworth library.

    pip install django-cravensworth

Install Cravensorth core in the installed apps list in your `settings.py`.

    INSTALLED_APPS = [
        ...
        'cravensworth.core',
    ]

Add Cravensworth middleware to the list of middleware in your `settings.py`.

    MIDDLEWARE = [
        ...
        'cravensworth.core.middleware.cravensworth_middleware',
        ...
    ]

If using Cravensworth in a web environment, ensure that the Django request
context processor is installed in your `TEMPLATES` configuration.

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'django.template.context_processors.request',
                    ...
                ],
            },
        },
    ]
