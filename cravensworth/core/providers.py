from abc import ABC, abstractmethod
from operator import itemgetter
from typing import Iterable

from django.http import HttpRequest
from django.utils.module_loading import import_string

from cravensworth.core.conf import get_setting
from cravensworth.core.models import Allocation, Audience, Context, Experiment
from cravensworth.core.utils import get_tracking_key


class ContextProvider(ABC):
    """
    Base class for context providers.

    Context providers populate contexts.
    """

    @abstractmethod
    def context(self, **kwargs) -> Context:
        """
        Constructs a context.
        """
        raise NotImplementedError()


class DjangoRequestContextProvider(ContextProvider):
    """
    A context provider for Django environments.

    Pre-populates the context with the Django user (`user`) and tracking key for
    identifying anonymous users (`anonymous`).
    """

    def context(self, **kwargs) -> Context:
        """
        Constructs a `DjangoRequestContextProvider`.

        Args:
            **kwargs (dict[str, Any]): Arbitrary keyword arguments.
                - request (django.http.HttpRequest): Django request. Must be
                  passed as a keyword argument.
        """
        request = kwargs.get('request')
        if request is None or not isinstance(request, HttpRequest):
            raise ValueError(
                'Django request is required as a keyword argument to context()'
            )

        return Context(
            {
                'user': getattr(request, 'user', None),
                'anonymous': get_tracking_key(request),
            }
        )


DEFAULT_CONTEXT_PROVIDER = (
    'cravensworth.core.providers.DjangoRequestContextProvider'
)


def get_context_provider() -> ContextProvider:
    """
    Load and instantiate an instance of a context provider.
    """
    return import_string(
        get_setting('CONTEXT_PROVIDER', DEFAULT_CONTEXT_PROVIDER),
    )()


class Source(ABC):
    """
    Protocol for experiment sources.

    Classes implementing this protocol must provide a `load` method that returns
    an iterable of `Experiment` instances. This allows flexible sourcing of
    experiments from different backends (e.g., settings, database, API).
    """

    @abstractmethod
    def load(self) -> Iterable[Experiment]:
        """
        Loads all experiments that the project should be aware of.

        For projects that use cravensworth_middleware, `load()` will be called
        for every request.
        """
        raise NotImplementedError()


class SettingsSource(Source):
    """
    A source that loads experiments from a Django settings module.

    Expects the setting `EXPERIMENTS` to be a list of experiment specifications,
    each a dictionary containing:

    - `name` - The unique name of the experiment.
    - `identity` - The name of the context value to use as identity.
    - `variants` - A list of variant supported by the experiment.
    - `audiences` - A list of audiences and allocations for each.
    - `seed` (optional) - A seed for extra control over user hashing.

    Example experient spec:

        CRAVENSWORTH = {
            'EXPERIMENTS': [
                {
                    'name': 'super_cool_experiment',
                    'identity': 'random',
                    'variants': [
                        {'name': 'active'},
                        {'name': 'inactive'},
                        {'name': 'control'},
                    ],
                    'audiences': [
                        {
                            'rule': 'language == "en"',
                            'allocations': [
                                {'variant': 'active', 'percent': 50},
                                {'variant': 'inactive', 'percent': 0},
                                {'variant': 'control', 'percent': 50},
                            ],
                        },
                        {
                            'rule': None,
                            'allocations': [
                                {'variant': 'inactive', 'percent': 100},
                            ],
                        },
                    ],
                }
            ]
        }

    For instances where you want to use an experiment as a simple switch (always
    on or off for all users), this source provides some syntactic sugar to make
    defining switches easier:

        CRAVENSWORTH = {
            'EXPERIMENTS': [
                'cool_switch:on',
                'uncool_switch:off'
            ]
        }

    The above is equivalent to:

        CRAVENSWORTH = {
            'EXPERIMENTS': [
                {
                    'name': 'cool_switch',
                    'identity': 'random',
                    'variants': [
                        {'name': 'on'},
                        {'name': 'off'},
                    ],
                    'audiences': [
                        {
                            'rule': None,
                            'allocations': [
                                {'variant': 'on', 'percent': 100},
                            ],
                        },
                    ],
                }
            ]
        }
    """

    def load(self) -> Iterable[Experiment]:
        experiments = set()
        for experiment in get_setting('EXPERIMENTS', []):
            if type(experiment) is str:
                experiments.add(self._read_switch(experiment))
            else:
                experiments.add(self._read_object(experiment))
        return experiments

    @staticmethod
    def _read_object(experiment) -> Experiment:
        variants = tuple(
            itemgetter('name')(variant) for variant in experiment['variants']
        )
        audiences = []

        for audience in experiment['audiences']:
            rule = audience.get('rule')
            allocations = tuple(
                Allocation(
                    *itemgetter('variant', 'percent')(allocation),
                ).validate()
                for allocation in audience['allocations']
            )
            audiences.append(Audience(rule, allocations).validate())

        return Experiment(
            name=experiment['name'],
            identity=experiment['identity'],
            variants=variants,
            audiences=tuple(audiences),
            seed=experiment.get('seed'),
        ).validate()

    @staticmethod
    def _read_switch(value) -> Experiment:
        name, variant = value.rsplit(':', maxsplit=1)
        return Experiment(
            name,
            identity='random',
            variants=('on', 'off'),
            audiences=(
                Audience(
                    rule=None,
                    allocations=(Allocation(variant, percent=100).validate(),),
                ).validate(),
            ),
        ).validate()


def get_source() -> Source:
    return import_string(
        get_setting('SOURCE', 'cravensworth.core.providers.SettingsSource'),
    )()


__all__ = [
    'ContextProvider',
    'DjangoRequestContextProvider',
    'get_context_provider',
    'Source',
    'SettingsSource',
    'get_source',
]
