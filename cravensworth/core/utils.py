from datetime import timedelta
from uuid import uuid4
from django.http import HttpRequest, HttpResponse

from cravensworth.core.conf import get_setting


DEFAULT_TRACKING_COOKIE = '__cwtk'


def _tracking_cookie() -> str:
    return get_setting('TRACKING_COOKIE', DEFAULT_TRACKING_COOKIE)


def generate_tracking_key() -> str:
    """
    Generate a new tracking key.
    """
    return uuid4().hex


def get_tracking_key(request: HttpRequest) -> str:
    """
    Gets the tracking key from a request if it exists. If the tracking key does
    not exist, one will be created and added to the request, so it may be
    consumed later, if required.
    """
    tk = getattr(request, '_cravensworth_tk', None)
    if tk is None:
        tk = request.COOKIES.get(_tracking_cookie())
    if tk is None:
        tk = generate_tracking_key()
    setattr(request, '_cravensworth_tk', tk)
    return tk


def set_tracking_key(request: HttpRequest, response: HttpResponse):
    """
    Sets the current tracking key as a cookie on the provided response. If no
    key exists, a new one will be generated.
    """
    name = _tracking_cookie()
    value = get_tracking_key(request)
    response.set_cookie(
        name,
        value,
        max_age=timedelta(days=365),
        httponly=True,
        samesite='Lax',
    )


__all__ = []
