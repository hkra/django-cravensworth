from django.test import TestCase, override_settings

from cravensworth.core import models
from cravensworth.core.providers import SettingsSource


class TestSettingsSource(TestCase):
    source = SettingsSource()

    @override_settings(
        CRAVENSWORTH={
            'EXPERIMENTS': [
                'switch_syntax:on',
                {
                    'name': 'experimentitious',
                    'identity': 'user.id',
                    'seed': 'maseed',
                    'variants': [
                        {'name': 'active'},
                        {'name': 'inactive'},
                        {'name': 'control'},
                    ],
                    'audiences': [
                        {
                            'rule': 'locale == "en-US"',
                            'allocations': [
                                {'variant': 'active', 'percent': 10},
                                {'variant': 'inactive', 'percent': 80},
                                {'variant': 'control', 'percent': 10},
                            ],
                        },
                        {
                            'allocations': [
                                {'variant': 'inactive', 'percent': 100},
                            ]
                        },
                    ],
                },
            ],
        }
    )
    def test_experiment_construction(self):
        experiments = self.source.load()
        self.assertEqual(
            experiments,
            {
                models.Experiment(
                    name='switch_syntax',
                    identity='random',
                    variants=('on', 'off'),
                    seed='switch_syntax',
                    audiences=(
                        models.Audience(
                            rule=None,
                            allocations=(
                                models.Allocation(
                                    variant='on',
                                    percent=100,
                                ),
                            ),
                        ),
                    ),
                ),
                models.Experiment(
                    name='experimentitious',
                    identity='user.id',
                    variants=('active', 'inactive', 'control'),
                    seed='maseed',
                    audiences=(
                        models.Audience(
                            rule='locale == "en-US"',
                            allocations=(
                                models.Allocation(
                                    variant='active',
                                    percent=10,
                                ),
                                models.Allocation(
                                    variant='inactive',
                                    percent=80,
                                ),
                                models.Allocation(
                                    variant='control',
                                    percent=10,
                                ),
                            ),
                        ),
                        models.Audience(
                            rule=None,
                            allocations=(
                                models.Allocation(
                                    variant='inactive',
                                    percent=100,
                                ),
                            ),
                        ),
                    ),
                ),
            },
        )
