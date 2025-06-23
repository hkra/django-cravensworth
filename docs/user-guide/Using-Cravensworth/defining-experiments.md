# Defining experiments

To use an experiment in your application, you must first declare it by creating
an experiment specification. Where you do this varies depending on which
experiment source backend you choose to use.

Cravensworth core ships with one source backend implementation: settings source.
Settings source looks for experiment specifications in your project's
`settings.py`. We will use the settings source for examples, but the principles
are the same for all sources.

## Experiment specification

An experiment specification tells Cravensworth how an experiment should behave.
Let's look an an example:

    {
        "name": "experiment_1",
        "identity": "user.id",
        "seed": "experiment_1",
        "variants": [
            {"name": "treatment"},
            {"name": "inactive"},
            {"name": "control"},
        ],
        "audiences": [
            {
                "rule": 'locale == "en-US"',
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

There's a lot going on here, so let's break it down.

### Name

`name` is the name of the experiment. When you refer to this experiment in code,
this is the name you will use. Names can contain only the ASCII word characters:
`a-zA-Z0-9_`.

There is no limit on the length of name, but it is recommended that you keep
them short but descriptive.

### Identity

`identity` is the name of the Cravensworth context (not Django template context!
) value that is used to partition experiment participants into variants. That's
a mouthful and probably not very helpful, so let's look at some ways that you
might use identity to control how variants are determined.

#### Use case: users

If you are running an experiment and you want to be able to put independent
users into different variants, using an identifier that uniquely identifies a
user will do that.

For example, when you test a new feature, users will independenly be put into
separate variants randomly. Some users may see the new feature, some may not.

#### Use case: tenants

There may be cases where having all users independently placed into different
variants may not be desireable.

For example, if you are rolling out a new feature in some collaboration software
to enterprise customers, you likely want _all_ users within each enterprise to
fall within the same variant. Otherwise, some users may see the new features and
others may not! This could be very frustrating for your users.

To avoid such a situation, you would not use individual user identities, but an
identity shared by all users in the enterprise. A good candidate might be a
tenant ID. All users within the same tenant—given they all match the same
rule—will be put in the same variant. We'll talk about rules later.

#### Valid values

The value of `identity` can be any of the following:

* The key of an identifier in the context. Names must contain only ASCII word
  characters and underscores.
* The attribute path (in dot notation). In our example, we are accessing a
  context value named `user` (the Django user model), which has an attribute
  called `id`. Like context keys, each segment must contain only ASCII word
  characters and underscores.
* `random`. This is a special, reserved key. When `random` is speficied as the
   identity, a random value will be chosen for the identity when determining
   variant. The random value will only chosen once for a given context, so it is
   safe to call functions that get an experiment variant, e.g., `is_variant()`,
   as many times as you like during a context's lifetime (usually, the same as
   a request lifetime, if your application is a web app).
* `anonymous`. Anonymous is another special, reserved key. It is intended to be
   used when there may not be a suitable identity value. For example, if you
   want to run tests on individual users, but some or all of those users may be
   anonymous and, therefore, lack a user ID. `anonymous` uses a tracking key
   saved in a cookie or generates such a value/cookie if none exists.

To be used as an identity, values must be string serializable.

### Seed

`seed` is a string used to randomize identities. The default value for `seed`,
if not provided, is the name of the experiment.

Most of the time you will not need to specify a seed. But there are some
advanced use cases where it may be necessary:

* **Coordinating two or more experiments:** Normally, experiments are
  independent, and users are randomized so the same participant does not always
  fall in the same bucket (division of an audience), whenever the same identity
  is used. But there may be cases where you do want participants to be in the
  same bucket within a variant. By setting the same seed for related experiments
  you ensure consistency in the way users are put into variants between
  experiments. Using non-independent experiments in this way can make analysis
  difficult and have all sorts of unintended consequences if you are not
  careful. It is recommended that you avoid doing this unless you have no other
  choice.
* **Resetting an experiment:** If you messed up your experiment (e.g., there was
  a bug that caused something not to work for one of the variants, or you messed
  up the variant allocations) and you need need to reset an experiment, you can
  do so by changing the seed value. A new seed will cause users to be put into
  different buckets, so you can start your experiment again.

`seed` is not considered in experiments using the `random` identity. Setting it
will have no effect.

### Variants

`variants` is a list of all variants used in your experiment. Variant names must
contain only ASCII word characters and underscores. There is no length limit,
but it is recommended to keep them short.

### Audiences

`audiences` is an list of audiences for an experiment. An audience is a group of
experiment participants that you wish to treat separately from other groups. You
might want to show different variants to different audiences, or control how an
experiment is rolled out to different audiences.

Each experiment has one or more audiences. Each audience has a rule (with
exception of the last rule) and a list of allocations, which specify how to
partition participants into variants.

#### Rules

Rules are Python expressions that can be used to segment participants into
audiences. When determining the variant for a participant, each audience rule
will be executed, in sequence, until one evaluates to `True` or until the last
audience is reached. The last audience cannot have a rule because it is a
catch-all (or fallback) audience that must match all participants that did not
match a preceding audience.

In our example experiment, the first audience has the rule, `locale == "en-US"`.
This rule will match any participant that has the en-US locale.

!!! NOTE
    The example assumes that the Cravensworth context has been populated with a
    string value called  `locale` containing the current locale. This is not
    default behavior! With the exception of the Django user and tracking key you
    must provide context data yourself using a context provider.

Rules cannot contain just any old aritrary Python code. There are some
restrictions to make them safer.

* A rule may only reference values contained in the Cravensworth context.
* A rule may not call any function.
* List, set, and dictionary construction and comprehensions are limited to a max
  length of 10,000. This fuctionality is enabled as a convenience, so you can
  write rules like `locale in ['en-US', 'en-CA']`. Don't abuse it to do gross
  things!
* Rules must be boolean expressions. If a non-boolean value is returned, an
  error will be raised at the time of evaluation.

#### Allocations

`allocations` defines how variants are assigned to participants in the audience.
The total allocation is split into a space of one-hundred buckets. Each
individual allocation has an associated variant and represents a range of
buckets, expressed as a positive integer percentage. The sum of allocations must
be one-hundred percent.

When a experiment is evaluated for a given participant, the participant's
identity is computed as a value between 0 and 99, inclusive. The allocation that
the identity falls into determines the variant for the participant.

### Putting it all together

So now that you know all the parts, we can understand the full experiment
specification.

The experiment is called "experiment_1".

The participant identity uses the ID of the current user to determine the
variant within an audience. This means that this experiment should only be used
with authenticated users.

The seed is being explicitly set, although this is not necessary. The seed is
the same as the experiment name, so it should be independent of other
experiments.

There are three variants. Variant behavior can be whatever you want, but here
we're using some commonly-used concepts:

* `treatment` - The treatment variant. Participants will see the thing we are
    testing.
* `control` - The control variant. Participants will see existing functionality.
* `inactive` - A special variant that exists only so we can have treatment and
    control allocations of less than 50—remember that allocations must sum to
    100!

Our experiment has two audiences. The first is for users that have the en-US
locale active (maybe we are testing a new feature, and we don't have
translations ready yet). 10 percent of participants will see the new
functionality. 10 percent are a control. 80% of users are not used (yet). If we
increase the test and control allocations in the future, some of that 80% will
be allocated to each of the other variants.

The second audience is the catch-all audience. Any users that aren't using the
en-US locale will fall into this audience. In this case, we've set an allocation
of 100% inactive, so we should not show these users the new thing we're testing.

## Switch specification

Cravensworth is primarily intended for experimentation, but sometimes you just
want to be able to turn stuff on and off—commonly called feature flags. It's
easy to to do this with experiments, but it is cumbersome to define an entire
experiment specification for a simple switch.

The settings source provides an easy shorthand for defining switches:

    'my_switch_name:on'  # or 'off' if the switch is off

This is equivalent to the following experiment specification:

    {
        "name": "my_switch_name",
        "identity": "random",
        "variants": [
            {"name": "on"},
            {"name": "off"},
        ],
        "audiences": [
            {
                "allocations": [
                    { "variant": "on", "percent": 100 },
                ]
            }
        ]
    }
