from abc import abstractmethod, ABC
from collections import UserDict
from dataclasses import dataclass
import logging
import random
import re
from typing import ClassVar, Iterable, Mapping, TypeVar, Protocol

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.utils.module_loading import import_string

from rapidhash import rapidhash
from simpleeval import EvalWithCompoundTypes

from cravensworth.core.conf import get_setting
from cravensworth.core.utils import get_tracking_key


logger = logging.getLogger(__name__)


class Context(UserDict):
    """
    Context contains contextual data for use by experiments in determining
    matching variants.
    """

    def __init__(self, data: dict = {}):
        super().__init__(data)
        self._identities = dict()

    def identity(self, keypath: str, seed: str | None) -> int:
        """
        Uses context data to calculate an identity for the given keypath and
        seed.

        Args:
            keypath (str): A path to specifying the key of the value in the
                context that is to be used as the identity. Paths are in object
                notation (period-delimited).
            seed (str, optional): A seed value that is combined with the key to
                produce an identity.

        `keypath` has a special value, "random", that will return a random value
        for use as the identity. Seed has no effect if "random" is used as the
        keypath.

        Identity values are cached so, the same keypath/seed pair will not be
        re-calculated if identity() is called again.

        Raises:
            KeyError: If the keypath does not exist in the context or its
                corresponding value is None.
        """
        cachekey = f'{keypath}{seed or ""}'
        if cachekey not in self._identities:
            self._identities[cachekey] = self._calculate_identity(keypath, seed)
        return self._identities[cachekey]

    def _calculate_identity(self, keypath, seed) -> int:
        if keypath == 'random':
            return random.randint(0, 99)
        identity = self._get_key_by_path(self, keypath)
        if identity is None:
            raise KeyError(
                f'Identity keypath "{keypath}" not found in the context, or the'
                'value is None'
            )
        return rapidhash(f'{identity}{seed}'.encode()) % 100

    @staticmethod
    def _get_key_by_path(obj, path):
        keys = path.split('.')
        current = obj
        for key in keys:
            if isinstance(current, Mapping):
                current = current.get(key)
            else:
                current = getattr(current, key, None)
            if current is None:
                break
        return current


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
                - request (django.http.HttpRequest): Django request. Must be passed
                as a keyword argument.
        """
        request = kwargs.get('request')
        if request is None or not isinstance(request, HttpRequest):
            raise ValueError(
                'Django request is required as a keyword argument to context()'
            )

        return Context(
            {
                'user': request.user,
                'anonymous': get_tracking_key(request),
            }
        )


DEFAULT_CONTEXT_PROVIDER = (
    'cravensworth.core.experiment.DjangoRequestContextProvider'
)


def get_context_provider() -> ContextProvider:
    """
    Load and instantiate an instance of a context provider.
    """
    return import_string(
        get_setting('CONTEXT_PROVIDER', DEFAULT_CONTEXT_PROVIDER),
    )()


_symbol_pattern = re.compile(r'^[\w\.]+$', re.ASCII)
_name_pattern = re.compile(r'^[\w]+$', re.ASCII)


T = TypeVar('T', bound='_Validatable')


class _Validatable(Protocol):
    def validate(self: T) -> T:
        for name, _ in self.__dataclass_fields__.items():
            validate = getattr(self, f'validate_{name}', None)
            if validate is not None and callable(validate):
                validate()
        return self


@dataclass(frozen=True, eq=True)
class Allocation(_Validatable):
    """
    Allocation represents the portion of an audience that is allocated to a
    particular variant.
    """

    variant: str
    percent: int

    def validate_variant(self):
        if not _name_pattern.match(self.variant):
            raise ValueError('Variant must contain only [a-zA-Z0-9_]')

    def validate_percent(self):
        if self.percent < 0:
            raise ValueError('Percent must not be negative')
        if self.percent > 100:
            raise ValueError('Percent must not be greater than 100')


@dataclass(frozen=True, eq=True)
class Audience(_Validatable):
    """
    An audience is a population of entities that all share a matching set of
    characteristics or, in the case of a default rule, no matching
    characteristics.

    Entities within an audience are assigned to an allocation based on their
    respective identities.
    """

    rule: str | None
    allocations: tuple[Allocation]
    evaluator: ClassVar[EvalWithCompoundTypes] = EvalWithCompoundTypes()

    def __post_init__(self):
        if self.rule is not None:
            try:
                object.__setattr__(
                    self, '_rule_parsed', self.evaluator.parse(self.rule)
                )
            except SyntaxError as e:
                raise ValueError('Invalid rule syntax') from e

    def validate_allocations(self):
        percent_total = 0
        for allocation in self.allocations:
            allocation.validate()
            percent_total += allocation.percent

        if percent_total != 100:
            raise ValueError('Allocations must sum to 100 percent')

    def matches(self, context: Context) -> bool:
        """
        Tests an entity to see if it matches the rule for inclusion in the
        audience.
        """
        if self.rule is None:
            return True
        self.evaluator.names = context
        result = self.evaluator.eval(self.rule, self._rule_parsed)
        if type(result) is not bool:
            raise TypeError('Audience rule must evaluate to a boolean value')
        return result

    def determine_variant(self, rangekey: int) -> str:
        """
        Determines the variant that matches a given entity based on the position
        of its identity within the range of allocations within this audience.
        """
        range_start = -1
        for allocation in self.allocations:
            range_end = range_start + allocation.percent
            if range_start < rangekey <= range_end:
                return allocation.variant
            range_start = range_end


@dataclass(frozen=True, eq=True)
class Experiment(_Validatable):
    """
    Experiment represents a test that can be used to verify a hypothesis by
    bucketing entities into multiple variants.
    """

    name: str
    identity: str
    variants: tuple[str]
    audiences: tuple[Audience]
    seed: str | None = None

    def __post_init__(self):
        if self.seed is None:
            object.__setattr__(self, 'seed', self.name)

    def validate_name(self):
        if not _name_pattern.match(self.name):
            raise ValueError('Name must contain only [a-zA-Z0-9_]')

    def validate_variants(self):
        if len(self.variants) < 1:
            raise ValueError('Experiment must define at least one variant')

    def validate_identity(self):
        if self.identity == 'random':
            return True
        if not _symbol_pattern.match(self.identity):
            raise ValueError('Invalid identity symbol name "{self.identity}"')

    def validate_audiences(self):
        if len(self.audiences) == 0:
            raise ValueError('Experiment must define at least one audience')
        if any(audience.rule is None for audience in self.audiences[:-1]):
            raise ValueError('Only the last audience rule can be None')
        if self.audiences[-1].rule is not None:
            raise ValueError('Last audience must not define a rule')

        for audience in self.audiences:
            for allocation in audience.allocations:
                allocation.validate()
                if allocation.variant not in self.variants:
                    raise ValueError(
                        f'Undeclared variant "{allocation.variant}"',
                    )

    def determine_variant(self, context: Context, override: str | None) -> str:
        """
        Determines which variant an entity should use by matching them against
        audience rules.

        Audiences will be matched in the order in which they are defined.
        """
        if override is not None and override in self.variants:
            return override

        for audience in self.audiences:
            if audience.matches(context):
                identity = context.identity(self.identity, self.seed)
                return audience.determine_variant(identity)


class CravensworthState:
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


def set_state(request: HttpRequest, state: CravensworthState):
    """
    Sets experiment state on the given request.
    """
    request.META[CravensworthState] = state


def get_state(request: HttpRequest) -> CravensworthState:
    """
    Gets experiment state from the given request.
    """
    return request.META.get(CravensworthState)


def is_variant(
    request: HttpRequest, name: str, variant: str | list[str]
) -> bool:
    """
    Returns true if the determined variant for the current entity matches
    `variant` or one of the list of variants, if multiple.
    """
    state = get_state(request)
    if state is None:
        raise ImproperlyConfigured(
            'Cravensworth state was not found in the request. Verify that the '
            '"cravensworth.core" middleware is correctly installed in settings.'
        )
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


DEFAULT_CRAVENSWORTH_COOKIE = '__cw'


def extract_overrides(request: HttpRequest) -> dict[str, str]:
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


__all__ = [
    'Context',
    'ContextProvider',
    'DjangoRequestContextProvider',
    'Allocation',
    'Audience',
    'Experiment',
    'get_state',
    'is_on',
    'is_off',
]
