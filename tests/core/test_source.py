from django.test import TestCase, override_settings

from cravensworth.core import experiment
from cravensworth.core.source import SettingsSource


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
                experiment.Experiment(
                    name='switch_syntax',
                    identity='random',
                    variants=('on', 'off'),
                    seed='switch_syntax',
                    audiences=(
                        experiment.Audience(
                            rule=None,
                            allocations=(
                                experiment.Allocation(
                                    variant='on',
                                    percent=100,
                                ),
                            ),
                        ),
                    ),
                ),
                experiment.Experiment(
                    name='experimentitious',
                    identity='user.id',
                    variants=('active', 'inactive', 'control'),
                    seed='maseed',
                    audiences=(
                        experiment.Audience(
                            rule='locale == "en-US"',
                            allocations=(
                                experiment.Allocation(
                                    variant='active',
                                    percent=10,
                                ),
                                experiment.Allocation(
                                    variant='inactive',
                                    percent=80,
                                ),
                                experiment.Allocation(
                                    variant='control',
                                    percent=10,
                                ),
                            ),
                        ),
                        experiment.Audience(
                            rule=None,
                            allocations=(
                                experiment.Allocation(
                                    variant='inactive',
                                    percent=100,
                                ),
                            ),
                        ),
                    ),
                ),
            },
        )
