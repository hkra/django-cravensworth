# Configuration

Settings used to configure Cravensworth's behavior are contained in a top-level
dictionary in your `settings.py`, called `CRAVENSWORTH`.

    CRAVENSWORTH = {
        # Put your settings here.
    }

## Core Settings

<a id="source"></a>
`SOURCE` (str)
:   Import string specifying the experiment source to use. Defaults to
    `cravensworth.core.source.SettingsSource`.

<a id="enabled-ips"></a>
`ENABLED_IPS` (list[str])
:   A list of IP addresses. User agents making requests from designated IP
    addresses will be allowed to override experiment variants using the override
    cookie. Requests originating non-designated IPs will be ignored. Defaults to
    `None`, which allows overrides originating from any IP address.

    Restricting overrides to known, trusted addresses is highly recommended in
    a production environment.

`OVERRIDE_COOKIE` (str)
:   Sets the name of the cookie used for overriding experiment variants.
    Defaults to `__cw`.

`TRACKING_COOKIE` (str)
:   Sets the name of the cookie used for tracking keys for anonymous users.
    Defaults to `__cwtk`.

`CONTEXT_PROVIDER` (str)
:   Import string specifying the context provider to use. Defaults to
    `cravensworth.core.experiment.DjangoRequestContextProvider`.

## Settings source settings

The settings source loads the list of known experiments from a project's
settings module.

`EXPERIMENTS` (list[str | dict])
:   Required. A list of [experiment specifications](#experiment-specifications).

### Experiment specifications

Simple switches can be defined using switch shorthand. It makes it possible to
define switches without writing a full experiment specification. If you only
need to turn features on and off, then this is all you need.

    'EXPERIMENTS': [
        "crazy_cool_feature:on",
        "kinda_sorta_risky_feature:off",
        "still_in_development_feature:off"
    ]

Switches are simple. If you need more fine-grained functionality, you'll need to
write a full experiment specification.

    'EXPERIMENTS': [
        {
            "name": "experiment_1",
            "identity": "user.id",
            "seed": "seedy",
            "variants": [
                {"name": "active"},
                {"name": "inactive"},
                {"name": "control"},
            ],
            "audiences": [
                {
                    "rule": 'locale == "en-US"',
                    "allocations": [
                        { "variant": "active", "percent": 25 },
                        { "variant": "inactive", "percent": 50 },
                        { "variant": "control", "percent": 25 },
                    ]
                },
                {
                    "rule": 'locale == "fr-CA"',
                    "allocations": [
                        { "variant": "active", "percent": 10 },
                        { "variant": "inactive", "percent": 80 },
                        { "variant": "control", "percent": 10 },
                    ]
                },
                {
                    "allocations": [
                        { "variant": "inactive", "percent": 100 },
                    ]
                }
            ]
        }
    ]

For details on each field, refer to
[Experiment](../../api-reference/experiment.md) in the API reference.

The switch notation and full experiment notation can appear together in the same
list.
