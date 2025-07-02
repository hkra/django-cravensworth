# What is Cravensworth?

Cravensworth is a experimentation framework for Django.

Its design is heavily inspired by Indeed's experimentation tool,
[Proctor](https://engineering.indeedblog.com/blog/2013/10/announcing-proctor-open-source/).

!!! NOTE
    django-cravensworth is pre-release software. The APIs and functionality may
    undergo significant, breaking changes without warning.

## Why do we need another feature flipper?

Cravensworth is much more than just a feature flipper, but that's still a fair
question. Alternatives like django-waffle, django-flags, or gargoyle have been
around for a long time. They provide similar functionality and are battle
tested. So, why do we need yet another alternative?

Here'a s laundry list of things that come to mind.

### Complex and intrusive APIs

Django feature flag libraries tend to be build around database models. This
means that they are tightly coupled with the database and, by default, they
come with migrations and other things that will change your database. That's not
to say that storing switches in the database is bad, only that making changes to
a database should be an intentional, well-considered step, not out-of-the-box,
YOLO-let's-go functionality. Cravensworth requires no migrations out of the box,
and models are used _only_ for storing and retrieving model data[^1].

[^1]: See the roadmap regarding the future plan for database support.

Building around database models also comes with some interesting design side
effects. Existing libraries encourage putting _all sorts_ of interesting things
in data models, like code for loading and caching external data—things that
generally don't belong in a data model.

The APIs for conditionally enabling flags tend to be clunky, complicated, and
inflexible. Rather than make you memorize complex condition DSLs and their
built-ins, Cravensworth allows you to write simple Python expressions.

Some libraries distinguish between different types of flags (e.g., switch,
sample, flag). This complicates the API and data schema for little benefit.
Cravensworth provides only one type: experiment. Although the concept of a
"switch" exists in Cravensworth, it is only for convenience; switches _are_
experiments.

### Intrusive overrides

The way that libraries do overrides is inconsistent and pollutes the API of the
application (e.g., query parameters). They also lack important features, like
the ability to restrict use of overrides to known audiences.

## Experimentation support

Feature flag libraries provide switches, which can only be on or off. This may
be adequate for simple A/B tests, but not for more complex test types.
Cravensworth supports experiments with multiple variants, enabling its use in
multivariate tests. It also provides a simple way to export experiment state for
use in logging and collection of experiment data.

Other libraries use questionable techniques for determining and tracking variant
membership that may skew experiment results. Variant pinning using cookies, for
example, is problematic for experiment rollout. Cookies also don't track well
when a user moves between devices or browsers. Cravensworth uses hashing with a
flexible identification strategy for determining user variants. This ensures
that users are assigned stable variants based on their identities, without the
use of cookies for storing variants. This is especially useful when a request
object is not available (in a background job, for example).

## Why doesn't it support {feature}?

We are yet in baby times, here. Not all planned features are implementated, and
it's possible not all needed features are known or planned.

If you think something important is missing, check if it's in the
[Roadmap](roadmap.md). If it's not there, create an issue to start a discussion.

## Getting started

Happy experimenting!
