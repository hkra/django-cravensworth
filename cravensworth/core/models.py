import random
import re
from collections import UserDict
from dataclasses import dataclass
from typing import ClassVar, Mapping, Protocol, TypeVar

from rapidhash import rapidhash
from simpleeval import EvalWithCompoundTypes


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


__all__ = [
    'Context',
    'Allocation',
    'Audience',
    'Experiment',
]
