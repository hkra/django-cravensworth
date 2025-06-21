from typing import Any, ParamSpec, TypeVar, Callable

from django.http import Http404
from django.shortcuts import redirect

from cravensworth.core import experiment


P = ParamSpec('P')
R = TypeVar('R')


def variant(
    name: str, variant: str | list[str], redirect_to: Any = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Controls access to the decorated view based on the active variant of the
    given experiment.

    If the given variant or variants are active, the view will be executed. If
    the variant is not a match, the user agent will be redirected to the
    specified redirect target, or will receive a 404 if no redirect is provided.

    Args:
        name (str): The name of the experiment.
        variant (str | list[str]): The name of the variant(s) that control
            access the view. Can be a single string (e.g., 'on') or a list of
            strings (e.g., `['variant_a', 'variant_b']`).
        redirect_to (Any, optional): If provided, the request will be redirected
            to this target if the active variant does not match the specified
            variant(s). If `None`, an `Http404` will be raised.

    `redirect_to` can be any type allowed by Django redirects:

    - A view name. `reverse()` will be used to get the redirect URL. Arguments
      are not supported.
    - A model that defines `get_absolute_url`.
    - An absolute or relative URL.

    Redirects are temporary (302).

    Returns:
        function: The decorated view function.

    Raises:
        Http404: If the active variant does not match the specified variant(s)
            and `redirect_to` is not provided.
    """

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        def wrapper(request, *args: P.args, **kwargs: P.kwargs) -> R:
            if experiment.is_variant(request, name, variant):
                return function(request, *args, **kwargs)
            elif redirect_to is not None:
                return redirect(redirect_to)
            raise Http404

        return wrapper

    return decorator


def switch_on(
    name: str, redirect_to: Any = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Controls access to the decorated view based on the active variant of the
    given experiment.

    If the active variant is 'on', the view will be executed. Otherwise the user
    agent will be redirected to the specified redirect target, or will receive
    a 404 if no redirect is provided.

    Args:
        name (str): The name of the experiment.
        redirect_to (Any, optional): If provided, the request will be redirected
            to this target if the active variant does not match the specified
            variant(s). If `None`, an `Http404` will be raised.

    `redirect_to` can be any type allowed by Django redirects:

    - A view name. `reverse()` will be used to get the redirect URL. Arguments
      are not supported.
    - A model that defines `get_absolute_url`.
    - An absolute or relative URL.

    Redirects are temporary (302).

    Returns:
        function: The decorated view function.

    Raises:
        Http404: If the experiment is off and `redirect_to` is not provided.
    """
    return variant(name, 'on', redirect_to)


def switch_off(
    name: str, redirect_to: Any = None
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Controls access to the decorated view based on the active variant of the
    given experiment.

    If the active variant is 'off', the view will be executed. Otherwise the
    user agent will be redirected to the specified redirect target, or will
    receive a 404 if no redirect is provided.

    Args:
        name (str): The name of the experiment.
        redirect_to (Any, optional): If provided, the request will be redirected
            to this target if the active variant does not match the specified
            variant(s). If None (default), an Http404 will be raised.

    `redirect_to` can be any type allowed by Django redirects:

    - A view name. `reverse()` will be used to get the redirect URL. Arguments
      are not supported.
    - A model that defines `get_absolute_url`.
    - An absolute or relative URL.

    Redirects will be temporary only (302).

    Returns:
        function: The decorated view function.

    Raises:
        Http404: If the experiment is on and `redirect_to` is not provided.
    """
    return variant(name, 'off', redirect_to)
