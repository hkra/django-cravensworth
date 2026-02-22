from django.test import RequestFactory, SimpleTestCase, override_settings

from testapp import views


class TestVariant(SimpleTestCase):
    factory = RequestFactory()

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': [
                {
                    'name': 'exp_1',
                    'identity': 'random',
                    'variants': [
                        {'name': 'active'},
                        {'name': 'inactive'},
                        {'name': 'control'},
                    ],
                    'audiences': [
                        {
                            'rule': None,
                            'allocations': [
                                {'variant': 'active', 'percent': 100},
                            ],
                        },
                    ],
                }
            ]
        }
    )
    def test_single_variant(self):
        request = self.factory.get('/templates/variant-single/')
        response = views.variant_single_view(request)
        self.assertContains(response, ':ACTIVE:')

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': [
                {
                    'name': 'exp_1',
                    'identity': 'random',
                    'variants': [
                        {'name': 'active'},
                        {'name': 'inactive'},
                        {'name': 'control'},
                    ],
                    'audiences': [
                        {
                            'rule': None,
                            'allocations': [
                                {'variant': 'active', 'percent': 100},
                            ],
                        },
                    ],
                }
            ]
        }
    )
    def test_variant_else(self):
        request = self.factory.get('/templates/variant-else/')
        response = views.variant_else_view(request)
        self.assertContains(response, ':ELSE:')

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': [
                {
                    'name': 'exp_1',
                    'identity': 'random',
                    'variants': [
                        {'name': 'one'},
                        {'name': 'two'},
                        {'name': 'three'},
                        {'name': 'four'},
                        {'name': 'five'},
                    ],
                    'audiences': [
                        {
                            'rule': None,
                            'allocations': [
                                {'variant': 'four', 'percent': 100},
                            ],
                        },
                    ],
                }
            ]
        }
    )
    def test_multiple_variants(self):
        request = self.factory.get('/templates/variant-multiple/')
        response = views.variant_multiple_view(request)
        self.assertContains(response, ':THREE-FOUR:')

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': [
                {
                    'name': 'exp_1',
                    'identity': 'random',
                    'variants': [
                        {'name': 'active'},
                        {'name': 'inactive'},
                    ],
                    'audiences': [
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
    )
    def test_no_match(self):
        request = self.factory.get('/templates/variant-none/')
        response = views.variant_none_view(request)
        self.assertNotContains(response, ':ACTIVE:')

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': [
                {
                    'name': 'exp_1',
                    'identity': 'random',
                    'variants': [
                        {'name': 'active'},
                        {'name': 'inactive'},
                    ],
                    'audiences': [
                        {
                            'rule': None,
                            'allocations': [
                                {'variant': 'active', 'percent': 100},
                            ],
                        },
                    ],
                }
            ]
        }
    )
    def test_variables(self):
        request = self.factory.get('/templates/variant-variable/')
        response = views.variant_variable_view(request)
        self.assertContains(response, ':ACTIVE:')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': []})
    def test_unknown_experiment(self):
        request = self.factory.get('/templates/variant-unknown/')
        response = views.variant_unknown_view(request)
        self.assertNotContains(response, ':UNKNOWN:')
        self.assertContains(response, ':ELSE:')


class TestSwitchOn(SimpleTestCase):
    factory = RequestFactory()

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_single(self):
        request = self.factory.get('/templates/on-single/')
        response = views.switchon_single_view(request)
        self.assertContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_single(self):
        request = self.factory.get('/templates/on-single/')
        response = views.switchon_single_view(request)
        self.assertNotContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_double(self):
        request = self.factory.get('/templates/on-double/')
        response = views.switchon_double_view(request)
        self.assertContains(response, 'ON')
        self.assertNotContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_double(self):
        request = self.factory.get('/templates/on-double/')
        response = views.switchon_double_view(request)
        self.assertNotContains(response, 'ON')
        self.assertContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_variable(self):
        request = self.factory.get('/templates/on-variable/')
        response = views.switchon_variable_view(request)
        self.assertContains(response, 'ON')

    @override_settings(
        CRAVENSWORTH={
            'SWITCHES': [
                {'name': 'active', 'on': True},
                {'name': 'inactive', 'on': False},
            ],
        }
    )
    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': ['active:on', 'inactive:off'],
        }
    )
    def test_switch_template_content(self):
        request = self.factory.get('/templates/on-content/')
        response = views.switchon_content_view(request)
        self.assertContains(response, ':ACTIVE-ON:')
        self.assertContains(response, ':INACTIVE-OFF:')
        self.assertNotContains(response, ':INACTIVE-ON:')


class TestSwitchOff(SimpleTestCase):
    factory = RequestFactory()

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_single(self):
        request = self.factory.get('/templates/off-single/')
        response = views.switchoff_single_view(request)
        self.assertContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_single(self):
        request = self.factory.get('/templates/off-single/')
        response = views.switchoff_single_view(request)
        self.assertNotContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_double(self):
        request = self.factory.get('/templates/off-double/')
        response = views.switchoff_double_view(request)
        self.assertContains(response, 'OFF')
        self.assertNotContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_double(self):
        request = self.factory.get('/templates/off-double/')
        response = views.switchoff_double_view(request)
        self.assertNotContains(response, 'OFF')
        self.assertContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_variable(self):
        request = self.factory.get('/templates/off-variable/')
        response = views.switchoff_variable_view(request)
        self.assertContains(response, 'OFF')

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': ['active:on', 'inactive:off'],
        }
    )
    def test_switch_template_content(self):
        request = self.factory.get('/templates/off-content/')
        response = views.switchoff_content_view(request)
        self.assertNotContains(response, ':ACTIVE-OFF:')
        self.assertContains(response, ':INACTIVE-OFF:')
        self.assertNotContains(response, 'INACTIVE-ON')
