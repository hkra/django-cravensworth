# What is Cravensworth?

Cravensworth is a experimentation framework for Django.

Its design is heavily inspired by Indeed's experimentation tool,
[Proctor](https://engineering.indeedblog.com/blog/2013/10/announcing-proctor-open-source/).

!!! NOTE
    django-cravensworth is pre-release software. The APIs and functionality may
    undergo significant, breaking changes without warning.

## Why do we need another feature flipper?

Alternatives like django-waffle, django-flags, or gargoyle have been around for
a long time. They provide similar functionality and are battle tested. So, why
do we need yet another alternative?

Cravensworth is designed to address common limitations of these libraries.
Cravensworth is more than just a feature flipper; it's built for experimentation
and flexible control over your applications.

Here's how Cravensworth stands apart:

### Simplified and Non-Intrusive Design

Many Django feature flag libraries tie switches directly to database models,
leading to:

* Mandatory Database Migrations: Cravensworth requires no migrations out of
  the box. Database models are[^1] used exclusively for data storage and
  retrieval, ensuring database changes are intentional and controlled.

  [^1]: Planned functionality. See the roadmap for future database support
        plans.

* Overloaded Data Models: Other libraries can encourage placing business logic
  or caching within data models, which complicates maintainability. Cravensworth
  promotes clean separation of concerns.

* Clunky APIs: Instead of forcing you to memorize complex Domain Specific
  Languages (DSLs) for conditional logic, Cravensworth lets you to use simple
  Python expressions.

* Fewer Flag Types: Some libraries distinguish between different types of flags
  (e.g., switch, sample, flag). This complicates. Cravensworth provides only one
  type: experiment. Although the concept of a "switch" exists in Cravensworth,
  it is only for convenience; switches _are_ experiments.

### Less Intrusive Overrides

Cravensworth provides a robust override mechanism that avoids the pollution of
your APIs and offers the ability to restrict override capabilites to known
audiences.

### Advanced Experimentation Capabilities

Cravensworth is built for experimentation:

* Multivariant Support: Run multivariate tests with multiple experiment
  variants.

* Data Export: Cravensworth allows the export of experiment state so you can
  integrate with whatever logging or data collection tools you use.

* Reliable Variant Assignment: Other libraries may rely on unreliable techniques
  like cookie-based variant pinning, which can skew results and doesn't work
  well across multiple devices. Cravensworth uses a hashing strategy to ensure
  stable variant assignments based on identities, even when a request object
  isn't available (e.g., in background jobs), leading to more accurate and
  reliable experiment results.

## Why doesn't it support {feature}?

We are yet in baby times, here. Not all planned features are implementated, and
it's possible not all needed features are known.

If you think something important is missing, check if it's in the
[Roadmap](roadmap.md). If it's not there, start a discussion by creating an
issue on GitHub.

## Getting started

It's time to make your monster. Happy experimenting!
