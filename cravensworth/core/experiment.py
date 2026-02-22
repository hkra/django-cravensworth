import logging
from typing import Iterable

from django.http import HttpRequest

from cravensworth.core.conf import get_setting
from cravensworth.core.models import Context, Experiment
from cravensworth.core.providers import get_context_provider, get_source


logger = logging.getLogger(__name__)


class _CravensworthState:
    """
    A container for holding the experiment state for a particular entity within
    a given lifetime (e.g., a single request).
    """

    def __init__(
        self,
        experiments: Iterable[Experiment],
        overrides: dict[str, str],
        context: Context,
    ):
        self._experiments = {e.name: e for e in experiments}
        self._overrides = overrides
        self._context = context

    def is_variant(self, name: str, variant: str | list[str]) -> bool:
        """
        Returns true if the determined variant for the current entity matches
        `variant` or one of the list of variants, if multiple.
        """
        experiment = self._experiments.get(name)
        if experiment is None:
            logger.warning(
                'is_variant was called for an undeclared experiment "%s". If '
                'this is a valid experiment, ensure that it exists in your'
                'experiment source and is correctly configured. Returning non-'
                'match.',
                name,
            )
            return False

        override = self._overrides.get(experiment.name)
        active_variant = experiment.determine_variant(self._context, override)
        return active_variant in (
            variant if isinstance(variant, list) else [variant]
        )

    def export(self) -> dict[str, str]:
        state = {}
        for experiment in self._experiments.values():
            override = self._overrides[experiment.name]
            state[experiment.name] = experiment.determine_variant(
                self._context,
                override,
            )
        return state


DEFAULT_CRAVENSWORTH_COOKIE = '__cw'


def _extract_overrides(request: HttpRequest) -> dict[str, str]:
    """
    Extracts experiment overrides from the given request and returns them as
    a mapping of experiment to overridden variant.

    This method takes into account whether the application has configured IP
    restriction. If IP restriction is enabled and the IP address does not match
    the list of allowed IPs, overrides will be empty.
    """
    enabled_ips = get_setting('ENABLED_IPS', None)
    restrict_ips = enabled_ips is not None
    overrides = {}

    if not restrict_ips or request.META['REMOTE_ADDR'] in enabled_ips:
        cookie_name = get_setting(
            'OVERRIDE_COOKIE', DEFAULT_CRAVENSWORTH_COOKIE
        )
        cookie = request.COOKIES.get(cookie_name)
        if cookie is not None:
            for override in cookie.split():
                experiment, variant = override.rsplit(':', maxsplit=1)
                overrides[experiment] = variant

    return overrides


class _StateResolver:
    def __init__(self):
        self.source = get_source()
        self.context_provider = get_context_provider()

    def resolve(self, request):
        experiments = self.source.load()
        overrides = _extract_overrides(request)
        context = self.context_provider.context(request=request)
        return _CravensworthState(experiments, overrides or {}, context)


_state_resolver = _StateResolver()


def set_state(request: HttpRequest, state: _CravensworthState):
    """
    Sets experiment state on the given request.
    """
    setattr(request, '_cravensworth_state', state)


def get_state(request: HttpRequest) -> _CravensworthState:
    """
    Gets experiment state from the given request.
    """
    if not hasattr(request, '_cravensworth_state'):
        set_state(request, _state_resolver.resolve(request))
    return getattr(request, '_cravensworth_state', None)


def is_variant(
    request: HttpRequest, name: str, variant: str | list[str]
) -> bool:
    """
    Returns true if the determined variant for the current entity matches
    `variant` or one of the list of variants, if multiple.
    """
    state = get_state(request)
    return state.is_variant(name, variant)


def is_on(request: HttpRequest, name: str) -> bool:
    """
    Returns True if the named switch is on; false otherwise.
    """
    return is_variant(request, name, 'on')


def is_off(request: HttpRequest, name: str) -> bool:
    """
    Returns True if the named switch is off; false otherwise.
    """
    return is_variant(request, name, 'off')


__all__ = [
    'is_variant',
    'is_on',
    'is_off',
]
