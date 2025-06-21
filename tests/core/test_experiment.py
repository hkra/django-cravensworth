from dataclasses import dataclass
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, SimpleTestCase, override_settings

from cravensworth.core.experiment import (
    DEFAULT_CRAVENSWORTH_COOKIE,
    Allocation,
    Audience,
    Context,
    CravensworthState,
    DjangoRequestContextProvider,
    Experiment,
    extract_overrides,
    is_variant,
)


class TestContext(SimpleTestCase):
    def test_random_identity(self):
        context = Context()
        identity = context.identity('random', None)
        self.assertTrue(0 <= identity < 100)

    def test_random_identity_cached(self):
        context = Context()
        identity1 = context.identity('random', None)
        identity2 = context.identity('random', None)
        self.assertEqual(identity1, identity2)

    @dataclass
    class ValueObject:
        value: str

    def test_valid_idenity_keypath_value(self):
        context = Context(
            {
                'a': '123',
                'b': {'c': 456, 'd': self.ValueObject(value='a')},
                'c': {3},
                'd': 42,
                'e': self.ValueObject(value='z'),
            }
        )
        keys = ['a', 'b.c', 'b.d.value', 'c', 'd', 'e.value']
        for key in keys:
            context.identity(key, None)  # Does not raise KeyError

    def test_idenity_raises_if_value_not_found(self):
        keys = ['j', 'a.z', 'b.y', 'b.c.x']
        context = Context(
            {
                'a': '123',
                'b': {'c': '456'},
            }
        )
        for key in keys:
            with self.assertRaises(KeyError):
                context.identity(key, None)

    def test_identities_differ_when_seeded(self):
        context = Context({'a': '123'})
        identity1 = context.identity('a', 'seed1')
        identity2 = context.identity('a', 'seed2')
        self.assertNotEqual(identity1, identity2)


class TestDjangoContextProvider(SimpleTestCase):
    factory = RequestFactory()
    provider = DjangoRequestContextProvider()

    def test_request_missing(self):
        with self.assertRaisesRegex(ValueError, 'request is required'):
            self.provider.context()

    def test_populates_anonymous_request(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        context = self.provider.context(request=request)

        user = context.get('user')
        tracking_key = context.get('anonymous')
        self.assertTrue(user is not None and user.is_anonymous)
        self.assertTrue(tracking_key is not None and tracking_key != '')

    def test_populates_authenticated_request(self):
        request = self.factory.get('/')
        request.user = User()
        context = self.provider.context(request=request)

        user = context.get('user')
        tracking_key = context.get('anonymous')
        self.assertTrue(user is not None and not user.is_anonymous)
        self.assertTrue(tracking_key is not None and tracking_key != '')


class TestAllocation(SimpleTestCase):
    def test_validate_valid_allocation(self):
        Allocation(variant='blue', percent=0).validate()
        Allocation(variant='red', percent=20).validate()
        Allocation(variant='green', percent=100).validate()

    def test_validate_invalid_variant_name_raises(self):
        for variant in [*r' ~!@#$%^&*()`-+=[]{};:<>,./?"', "'", '']:
            with self.assertRaisesRegex(
                ValueError, 'Variant must contain only'
            ):
                Allocation(variant=variant, percent=50).validate()

    def test_validate_negative_percent_raises(self):
        with self.assertRaisesRegex(ValueError, 'negative'):
            Allocation(variant='blue', percent=-20).validate()

    def test_validate_percent_too_big_raises(self):
        with self.assertRaisesRegex(ValueError, 'greater than 100'):
            Allocation(variant='blue', percent=110).validate()


class TestAudience(SimpleTestCase):
    def test_validate_rule_syntax_error(self):
        with self.assertRaisesRegex(ValueError, 'Invalid rule'):
            Audience(
                rule=')()()(',
                allocations=[
                    Allocation('blue', percent=100),
                ],
            ).validate()

    def test_validate_valid_rule_syntax(self):
        Audience(
            rule='user.id == 12',
            allocations=[
                Allocation('blue', percent=100),
            ],
        ).validate()

    def test_validate_allocations_less_than_100_percent(self):
        with self.assertRaisesRegex(ValueError, '100 percent'):
            Audience(
                rule=None,
                allocations=[
                    Allocation('blue', percent=10),
                    Allocation('red', percent=10),
                ],
            ).validate()

    def test_validate_allocations_greater_than_100_percent(self):
        with self.assertRaisesRegex(ValueError, '100 percent'):
            Audience(
                rule=None,
                allocations=[
                    Allocation('red', percent=11),
                    Allocation('green', percent=90),
                ],
            ).validate()

    def test_matches_default_rule(self):
        audience = Audience(
            rule=None,
            allocations=[
                Allocation('red', percent=100),
            ],
        ).validate()
        self.assertTrue(audience.matches({}))

    def test_matches_raises_for_non_bool_result(self):
        audience = Audience(
            rule='1 + 1',
            allocations=[
                Allocation('red', percent=100),
            ],
        )
        with self.assertRaises(TypeError):
            self.assertTrue(audience.matches({}))

    def test_matches_trivial_rules(self):
        rules = [
            ('True', True),
            ('not False', True),
            ('1 == 1', True),
            ('2 != 5', True),
            ('10 % 3 == 1', True),
            ('(1 + 2) * 5 == 15', True),
            ('200 > 199', True),
            ('1 >= 0', True),
            ('0 >= 0', True),
            ('42 < 45', True),
            ('44 <= 555', True),
            ('False', False),
            ('not True', False),
            ('1 != 1', False),
            ('2 == 5', False),
            ('10 % 3 == 2', False),
            ('(1 + 2) * 5 == 11', False),
            ('200 < 199', False),
            ('1 <= 0', False),
            ('42 > 45', False),
            ('44 >= 555', False),
        ]
        for rule, expected in rules:
            audience = Audience(
                rule,
                allocations=[
                    Allocation('red', percent=100),
                ],
            ).validate()
            self.assertEqual(audience.matches({}), expected)

    def test_matches_fancier_rules(self):
        rules = [
            ('name == "bojack"', {'name': 'bojack'}, True),
            ('name == "bojack"', {'name': 'sebastian'}, False),
            (
                'lang == "en" or country == "US"',
                {'lang': 'en', 'country': 'CA'},
                True,
            ),
            (
                'lang == "en" or country == "US"',
                {'lang': 'fr', 'country': 'CA'},
                False,
            ),
            (
                'lang == "en" and country == "US"',
                {'lang': 'en', 'country': 'US'},
                True,
            ),
            ('is_mobile', {'is_mobile': True}, True),
            ('is_mobile', {'is_mobile': False}, False),
            (
                'firstname != lastname',
                {'firstname': 'chad', 'lastname': 'chadington'},
                True,
            ),
            ('user.id > 100', {'user': {'id': 100}}, False),
            ('user.id > 100', {'user': {'id': 101}}, True),
            ('user["id"] > 100', {'user': {'id': 100}}, False),
            ('user["id"] > 100', {'user': {'id': 101}}, True),
            (
                'user.is_authenticated',
                {'user': {'is_authenticated': True}},
                True,
            ),
            ('not is_admin', {'is_admin': False}, True),
            ('not is_admin', {'is_admin': True}, False),
            (
                '(lang == "en" and country == "US") or is_admin',
                {'lang': 'en', 'country': 'FR', 'is_admin': True},
                True,
            ),
            (
                '(lang == "en" and country == "US") or is_admin',
                {'lang': 'en', 'country': 'US', 'is_admin': False},
                True,
            ),
            (
                '(lang == "en" and country == "US") or is_admin',
                {'lang': 'en', 'country': 'FR', 'is_admin': False},
                False,
            ),
            ('score >= 90', {'score': 95}, True),
            ('score >= 90', {'score': 85}, False),
            ('18 <= age < 65', {'age': 30}, True),
            ('18 <= age < 65', {'age': 70}, False),
            ('lang in ["en", "fr"]', {'lang': 'en'}, True),
            ('lang in ["en", "fr"]', {'lang': 'de'}, False),
            ('lang in {"en", "fr"}', {'lang': 'en'}, True),
            ('"lang" in {"lang": "de"}', {}, True),
            ('"lang" in properties', {'properties': {'lang': 'de'}}, True),
            ('"country" in properties', {'properties': {'lang': 'de'}}, False),
            ('balance - debt > 0', {'balance': 100, 'debt': 20}, True),
            ('balance - debt > 0', {'balance': 10, 'debt': 20}, False),
            (
                'profile.active and profile.email_verified',
                {'profile': {'active': True, 'email_verified': False}},
                False,
            ),
            (
                'profile.active and profile.email_verified',
                {'profile': {'active': True, 'email_verified': True}},
                True,
            ),
            ('tags.count > 0', {'tags': {'count': 2}}, True),
            ('tags.count > 0', {'tags': {'count': 0}}, False),
        ]
        for rule, names, expected in rules:
            audience = Audience(
                rule,
                allocations=[
                    Allocation('chartreuse', percent=100),
                ],
            ).validate()
            self.assertEqual(audience.matches(names), expected)

    def test_determine_variant(self):
        audience = Audience(
            None,
            allocations=[
                Allocation('red', percent=25),
                Allocation('green', percent=25),
                Allocation('blue', percent=25),
                Allocation('yellow', percent=25),
            ],
        ).validate()
        cases = [
            # Test key points at edges and between ranges.
            [0, 'red'],
            [1, 'red'],
            [24, 'red'],
            [25, 'green'],
            [37, 'green'],
            [49, 'green'],
            [50, 'blue'],
            [65, 'blue'],
            [74, 'blue'],
            [75, 'yellow'],
            [90, 'yellow'],
            [99, 'yellow'],
        ]
        for rangekey, expected_variant in cases:
            self.assertEqual(
                audience.determine_variant(rangekey), expected_variant
            )


class TestExperiment(SimpleTestCase):
    def test_seed_initialized_to_test_name_if_not_provided(self):
        name = 'experiment_mc_fancy_test'
        exp = Experiment(
            name=name,
            identity='tk',
            variants=['exuberant'],
            audiences=[
                Audience(None, [Allocation('exuberant', 100)]),
            ],
        ).validate()
        self.assertEqual(exp.seed, name)

    def test_validate_invalid_experiment_name_raises(self):
        for name in [*r' ~!@#$%^&*()`-+=[]{};:<>,./\?"', "'", '']:
            with self.assertRaisesRegex(ValueError, 'Name must contain only'):
                Experiment(
                    name=name,
                    identity='tk',
                    variants=['red'],
                    audiences=[
                        Audience(None, [Allocation('red', 100)]),
                    ],
                ).validate()

    def test_validate_no_variants(self):
        with self.assertRaisesRegex(
            ValueError, 'must define at least one variant'
        ):
            Experiment(
                name='experiment',
                identity='tk',
                variants=[],
                audiences=[
                    Audience(None, [Allocation('red', 100)]),
                ],
            ).validate()

    def test_validate_identity_random(self):
        Experiment(
            name='experiment',
            identity='random',
            variants=['red'],
            audiences=[
                Audience(None, [Allocation('red', 100)]),
            ],
        ).validate()

    def test_validate_invalid_identity_name(self):
        with self.assertRaisesRegex(ValueError, 'Invalid identity symbol name'):
            Experiment(
                name='experiment',
                identity='jkj_*33',
                variants=['gold'],
                audiences=[
                    Audience(None, [Allocation('gold', 100)]),
                ],
            ).validate()

    def test_validate_no_audiences(self):
        with self.assertRaisesRegex(ValueError, 'at least one audience'):
            Experiment(
                name='experiment',
                identity='random',
                variants=['silver'],
                audiences=[],
            ).validate()

    def test_validate_last_audience_rule_not_none(self):
        with self.assertRaisesRegex(
            ValueError, 'Last audience must not define a rule'
        ):
            Experiment(
                name='experiment',
                identity='random',
                variants=['silver'],
                audiences=[
                    Audience('user.id == 1', [Allocation('gold', 100)]),
                ],
            ).validate()

    def test_validate_multiple_none_rules(self):
        with self.assertRaisesRegex(
            ValueError, 'Only the last audience rule can be None'
        ):
            Experiment(
                name='experiment',
                identity='random',
                variants=['silver', 'gold'],
                audiences=[
                    Audience(None, [Allocation('silver', 100)]),
                    Audience(None, [Allocation('gold', 100)]),
                ],
            ).validate()

    def test_validate_audience_with_undeclared_variant(self):
        with self.assertRaisesRegex(ValueError, 'Undeclared variant'):
            Experiment(
                name='experiment',
                identity='random',
                variants=['gold'],
                audiences=[
                    Audience('user.id == 1', [Allocation('gold', 100)]),
                    Audience(None, [Allocation('ruby', 100)]),
                ],
            ).validate()

    def test_determine_variant(self):
        exp = Experiment(
            name='experiment',
            identity='random',
            variants=['gold', 'ruby'],
            audiences=[
                Audience('user.id == 1', [Allocation('gold', 100)]),
                Audience(None, [Allocation('ruby', 100)]),
            ],
        ).validate()
        context_ruby = Context({'user': User(id=0)})
        context_gold = Context({'user': User(id=1)})
        self.assertEqual(exp.determine_variant(context_ruby, None), 'ruby')
        self.assertEqual(exp.determine_variant(context_gold, None), 'gold')

    def test_determine_variant_override(self):
        exp = Experiment(
            name='experiment',
            identity='random',
            variants=['gold', 'ruby'],
            audiences=[
                Audience('user.id == 1', [Allocation('gold', 100)]),
                Audience(None, [Allocation('ruby', 100)]),
            ],
        ).validate()
        context_ruby = Context({'user': User(id=0)})
        context_gold = Context({'user': User(id=1)})
        self.assertEqual(exp.determine_variant(context_ruby, 'gold'), 'gold')
        self.assertEqual(exp.determine_variant(context_gold, 'ruby'), 'ruby')

    def test_determine_variant_ignores_unknown_variant_override(self):
        exp = Experiment(
            name='experiment',
            identity='random',
            variants=['gold', 'ruby'],
            audiences=[
                Audience('user.id == 1', [Allocation('gold', 100)]),
                Audience(None, [Allocation('ruby', 100)]),
            ],
        ).validate()
        context_ruby = Context({'user': User(id=0)})
        self.assertEqual(exp.determine_variant(context_ruby, 'wumbo'), 'ruby')


class TestExtractOverrides(SimpleTestCase):
    factory = RequestFactory()

    def test_no_overrides(self):
        request = self.factory.get('/')

        overrides = extract_overrides(request)
        self.assertEqual(overrides, {})

    def test_extracts_overrides(self):
        request = self.factory.get('/')
        request.COOKIES[DEFAULT_CRAVENSWORTH_COOKIE] = 'switch:on'

        overrides = extract_overrides(request)
        self.assertEqual(overrides, {'switch': 'on'})

    def test_multiple_overrides(self):
        request = self.factory.get('/')
        request.COOKIES[DEFAULT_CRAVENSWORTH_COOKIE] = (
            'experiment1:variant1 experiment2:variant2'
        )

        overrides = extract_overrides(request)
        self.assertEqual(
            overrides,
            {
                'experiment1': 'variant1',
                'experiment2': 'variant2',
            },
        )

    def test_duplicate_overrides(self):
        request = self.factory.get('/')
        request.COOKIES[DEFAULT_CRAVENSWORTH_COOKIE] = (
            'experiment:variant1 experiment:variant2'
        )

        overrides = extract_overrides(request)
        # We don't really care about duplicates. It'll be sorted out by the
        # state, where last one clobbers all.
        self.assertEqual(
            overrides,
            {
                'experiment': 'variant2',
            },
        )

    @override_settings(CRAVENSWORTH={'OVERRIDE_COOKIE': 'mycookie'})
    def test_custom_cookie_name(self):
        request = self.factory.get('/')
        request.COOKIES['mycookie'] = 'swank:active'

        overrides = extract_overrides(request)
        self.assertEqual(overrides, {'swank': 'active'})

    @override_settings(CRAVENSWORTH={'ENABLED_IPS': []})
    def test_ip_restricted_no_ips(self):
        request = self.factory.get('/')
        request.COOKIES[DEFAULT_CRAVENSWORTH_COOKIE] = 'switch:on'

        overrides = extract_overrides(request)
        self.assertEqual(overrides, {})

    @override_settings(CRAVENSWORTH={'ENABLED_IPS': ['127.0.0.1']})
    def test_ip_restricted_matching_ip(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.COOKIES[DEFAULT_CRAVENSWORTH_COOKIE] = 'switch:on'

        overrides = extract_overrides(request)
        self.assertEqual(overrides, {'switch': 'on'})

    @override_settings(CRAVENSWORTH={'ENABLED_IPS': ['127.0.0.1', '127.0.0.2']})
    def test_ip_restricted_unknown_ip(self):
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.3'
        request.COOKIES[DEFAULT_CRAVENSWORTH_COOKIE] = 'switch:on'

        overrides = extract_overrides(request)
        self.assertEqual(overrides, {})


class TestIsVariant(SimpleTestCase):
    factory = RequestFactory()

    def test_raises_when_state_is_missing(self):
        request = self.factory.get('/')
        with self.assertRaises(ImproperlyConfigured):
            is_variant(request, 'awesome', 'frangled')


class TestCravensworthState(SimpleTestCase):
    def test_returns_false_for_undeclared_experiment(self):
        state = CravensworthState(
            experiments=[],
            overrides={},
            context=Context(),
        )
        self.assertFalse(state.is_variant('bobobobobobobo', 'bam'))

    def test_is_variant_single_variant(self):
        state = CravensworthState(
            experiments=[
                Experiment(
                    name='a',
                    identity='random',
                    variants=['1', '2'],
                    audiences=[
                        Audience(rule=None, allocations=[Allocation('1', 100)])
                    ],
                )
            ],
            overrides={},
            context=Context(),
        )
        self.assertTrue(state.is_variant('a', '1'))
        self.assertFalse(state.is_variant('a', '2'))

    def test_is_variant_multiple_variants(self):
        state = CravensworthState(
            experiments=[
                Experiment(
                    name='a',
                    identity='random',
                    variants=['1', '2', '3'],
                    audiences=[
                        Audience(rule=None, allocations=[Allocation('1', 100)])
                    ],
                )
            ],
            overrides={},
            context=Context(),
        )
        self.assertTrue(state.is_variant('a', ['1', '2']))
        self.assertFalse(state.is_variant('a', ['2', '3']))

    def test_override(self):
        state = CravensworthState(
            experiments=[
                Experiment(
                    name='a',
                    identity='random',
                    variants=['1', '2'],
                    audiences=[
                        Audience(rule=None, allocations=[Allocation('1', 100)])
                    ],
                )
            ],
            overrides={'a': '2'},
            context=Context(),
        )
        self.assertFalse(state.is_variant('a', '1'))
        self.assertTrue(state.is_variant('a', '2'))
