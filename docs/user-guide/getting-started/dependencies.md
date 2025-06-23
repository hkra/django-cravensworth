# Dependencies

## Packages

Cravensworth has been tested with, and supports, the following.

* Python 3.10+
* Django 4.2+

## Django requirements

### Request

The [DjangoRequestContextProvider][cravensworth.core.experiment.DjangoRequestContextProvider]
requires that the request be available in the Django context.

If running an application that does not have access to a request object (e.g., a
background job or command), you must provide a context provider that can get the
context data required for your experiments.

### Users/Authentication

If using the `user` object in experiment rules, the `django.contrib.auth` app
should be [installed and configured](https://docs.djangoproject.com/en/dev/topics/auth/#installation)
in `settings.py`.

### Templates

Cravensworth template tags require the [Django templates backend](https://docs.djangoproject.com/en/dev/ref/settings/#templates)
with the request context processor.

Other template backends are not supported at this time.

### IP address restriction

IP restriction requires the remote address of the user agent. If your app is
sitting behind an intermediary, such as a load balancer or some other kind of
proxy, ensure that the intermediary is configured to forward remote addresses.
