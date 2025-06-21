from typing import overload, Any
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


_NotGiven = object()


@overload
def get_setting(path: str, default: Any) -> Any: ...
@overload
def get_setting(path: str) -> Any: ...


def get_setting(path: str, default: Any = _NotGiven):
    """
    Retrieves a cravensworth configuration setting.

    This is not for general Django settings. To get Django settings, use the
    settings object from django.conf directly.

    Args:
        path (str): The dotted path to the setting.
        default (Any, optional): A fallback value to return if the setting is
            not found. If not default is provided, an error will be raised.

    Returns:
        Any: The setting value, or `default` if not found and provided.

    Raises:
        ImproperlyConfigured: The setting is not found and no default is given.
    """
    cursor = getattr(settings, 'CRAVENSWORTH')
    for segment in path.split('.'):
        if segment in cursor:
            cursor = cursor.get(segment)
        else:
            if default == _NotGiven:
                raise ImproperlyConfigured(
                    f'Expected setting CRAVENSWORTH.{path} not found',
                )
            return default
    return cursor
