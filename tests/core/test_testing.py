from django.test import RequestFactory, SimpleTestCase, override_settings

from cravensworth.core.testing import override_experiment
from cravensworth.core.experiment import is_on


class TestOverrideExperiment(SimpleTestCase):
    factory = RequestFactory()

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_single_override(self):
        request = self.factory.get('/path')
        override_experiment(request, 'switch', 'on')

        self.assertTrue(is_on(request, 'switch'))

    @override_settings(
        CRAVENSWORTH={'EXPERIMENTS': ['switch1:off', 'switch2:on']}
    )
    def test_multiple_overrides(self):
        request = self.factory.get('/path')
        override_experiment(
            request,
            {
                'switch1': 'on',
                'switch2': 'off',
            },
        )

        self.assertTrue(is_on(request, 'switch1'))
        self.assertFalse(is_on(request, 'switch2'))

    def test_single_override_non_none_variant(self):
        request = self.factory.get('/path')

        with self.assertRaises(ValueError):
            override_experiment(request, 'switch', None)

    def test_multiple_overrides_non_dict_experiment(self):
        request = self.factory.get('/path')

        with self.assertRaises(TypeError):
            override_experiment(request, set('switch:on'))
