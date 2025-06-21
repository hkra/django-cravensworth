from django.test import Client, SimpleTestCase, override_settings


class TestVariant(SimpleTestCase):
    client = Client()

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
        response = self.client.get('/templates/variant-single/')
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
        response = self.client.get('/templates/variant-else/')
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
        response = self.client.get('/templates/variant-multiple/')
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
        response = self.client.get('/templates/variant-none/')
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
        response = self.client.get('/templates/variant-variable/')
        self.assertContains(response, ':ACTIVE:')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': []})
    def test_unknown_experiment(self):
        response = self.client.get('/templates/variant-unknown/')
        self.assertNotContains(response, ':UNKNOWN:')
        self.assertContains(response, ':ELSE:')


class TestSwitchOn(SimpleTestCase):
    client = Client()

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_single(self):
        response = self.client.get('/templates/on-single/')
        self.assertContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_single(self):
        response = self.client.get('/templates/on-single/')
        self.assertNotContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_double(self):
        response = self.client.get('/templates/on-double/')
        self.assertContains(response, 'ON')
        self.assertNotContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_double(self):
        response = self.client.get('/templates/on-double/')
        self.assertNotContains(response, 'ON')
        self.assertContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_variable(self):
        response = self.client.get('/templates/on-variable/')
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
        response = self.client.get('/templates/on-content/')
        self.assertContains(response, ':ACTIVE-ON:')
        self.assertContains(response, ':INACTIVE-OFF:')
        self.assertNotContains(response, ':INACTIVE-ON:')


class TestSwitchOff(SimpleTestCase):
    client = Client()

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_single(self):
        response = self.client.get('/templates/off-single/')
        self.assertContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_single(self):
        response = self.client.get('/templates/off-single/')
        self.assertNotContains(response, 'OFF')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_double(self):
        response = self.client.get('/templates/off-double/')
        self.assertContains(response, 'OFF')
        self.assertNotContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_switch_on_double(self):
        response = self.client.get('/templates/off-double/')
        self.assertNotContains(response, 'OFF')
        self.assertContains(response, 'ON')

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:off']})
    def test_switch_off_variable(self):
        response = self.client.get('/templates/off-variable/')
        self.assertContains(response, 'OFF')

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': ['active:on', 'inactive:off'],
        }
    )
    def test_switch_template_content(self):
        response = self.client.get('/templates/off-content/')
        self.assertNotContains(response, ':ACTIVE-OFF:')
        self.assertContains(response, ':INACTIVE-OFF:')
        self.assertNotContains(response, 'INACTIVE-ON')
