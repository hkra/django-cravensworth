from typing import overload

from django.http import HttpRequest

from cravensworth.core.conf import get_setting
from cravensworth.core.experiment import DEFAULT_CRAVENSWORTH_COOKIE


@overload
def override_experiment(request: HttpRequest, experiment: dict[str, str]): ...


@overload
def override_experiment(
    request: HttpRequest, experiment: str, variant: str
): ...


def override_experiment(
    request: HttpRequest,
    experiment: dict[str, str] | str,
    variant: str | None = None,
):
    """Override experiment variants on a request by setting the override cookie.

    This is useful in tests to make experiment behavior deterministic.

    Can be called with a single experiment name and variant::

        override_experiment(request, 'switch', 'on')

    Or with a dict to override multiple experiments at once::

        override_experiment(request, {'switch1': 'on', 'switch2': 'off'})

    Args:
        request: The Django request object to set the override cookie on.
        experiment: Either an experiment name (str) or a dict mapping
            experiment names to variant values.
        variant: The variant value when ``experiment`` is a str.
            Required when ``experiment`` is a str, ignored otherwise.

    Raises:
        ValueError: If ``experiment`` is a str and ``variant`` is None.
        TypeError: If ``experiment`` is neither a str nor a dict.
    """

    def make_override(name, value):
        return f'{name}:{value}'

    if isinstance(experiment, str):
        if variant is None:
            raise ValueError('variant must not be None')
        cookie = make_override(experiment, variant)

    elif isinstance(experiment, dict):
        cookie = ' '.join(
            make_override(name, value) for name, value in experiment.items()
        )

    else:
        raise TypeError('expected a string or a dictionary for experiment')

    cookie_name = get_setting('OVERRIDE_COOKIE', DEFAULT_CRAVENSWORTH_COOKIE)
    request.COOKIES[cookie_name] = cookie
