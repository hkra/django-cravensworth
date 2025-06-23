# Experiments in templates

Although it is possible to use experiments in templates by passing context to a
view template, it's a pain. Wouldn't it be nice if there were some convenient
template tags you could use to check experiment variants? Well, there are!

To use Cravensworth template tags, load the cravensworth module at the top of
your template.

    {% load cravensworth %}

## Checking variants

You can conditionally render templates based on variants using the `variant`
template tag.

    {% load cravensworth %}

    {% variant "experiment_name" "variant_A" "variant_B" %}
        Variant A or B was active!
    {% endvariant %}

The `variant` tag can also have `elif` and `else` blocks:

    {% variant "me_experimanto" "variant_A" %}
        Variant A was active!
    {% elif "variant_B" %}
        It was actually variant_B...
    {% else %}
        It was none of those...
    {% endvariant %}

## Checking switches

If an experiment is configured as a switch, you can check if the variant is "on"
or "off" using the `switch_on` and `switch_off` tags, respectively.

    {% load cravensworth %}

    {% switchon 'my_switch' %}
        The switch was on!
    {% endswitchon %}

Switch blocks can also have `else` blocks:

    {% switchon 'my_switch' %}
        The switch was on!
    {% else %}
        The switch was off!
    {% endswitchon %}
