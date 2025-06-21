from django import template
from django.template import Node, TemplateSyntaxError

from cravensworth.core.experiment import is_on, is_variant


register = template.Library()


class _VariantBranch:
    """
    Represents a single variant or elif branch within a variant template tag.

    This class holds the experiment name, the specific variants associated with
    this branch, and the nodelist to render if this branch is active.
    """

    def __init__(self, experiment_name_var, variant_vars, nodelist):
        self.experiment_name_var = experiment_name_var
        self.variant_vars = variant_vars
        self.nodelist = nodelist

    def is_active(self, context, request, experiment_name) -> bool:
        variants = []
        for variant_var in self.variant_vars:
            variant = variant_var.resolve(context)
            if isinstance(variant, (list, tuple)):
                variants.extend(variant)
            else:
                variants.append(variant)

        return is_variant(request, experiment_name, variants)

    def render(self, context):
        return self.nodelist.render(context)


class _VariantBlockNode(Node):
    """
    Represents a `variant` template tag and its various possible branches,
    similar to an if/elif/else block.
    """

    def __init__(self, experiment_name_var, branches, else_nodelist):
        self.experiment_name_var = experiment_name_var
        self.branches = branches
        self.else_nodelist = else_nodelist

    def render(self, context):
        request = context['request']
        experiment_name = self.experiment_name_var.resolve(context)

        for branch in self.branches:
            if branch.is_active(context, request, experiment_name):
                return branch.render(context)

        if self.else_nodelist:
            return self.else_nodelist.render(context)
        return ''


@register.tag('variant')
def variant(parser, token):
    """
    Renders content based on active experiment variants, similar to if/elif/
    else.

    `variant` and `elif` blocks can take one or more variant. If no named
    variants are active the else block, if provided, will be rendered.

    Example:

        {% variant "experiment_name" "variant_A" "variant_B" %}
            Content for variant A or B...
        {% elif "variant_C" %}
            Optional Content for variant C...
        {% else %}
            Optional fallback content...
        {% endvariant %}
    """
    args = token.split_contents()
    tag_name = args.pop(0)

    if len(args) < 2:
        raise TemplateSyntaxError(
            f"'{tag_name}' requires at least an experiment name and variant"
        )

    experiment_name_var = template.Variable(args.pop(0))
    variant_vars = [template.Variable(arg) for arg in args]
    branches = []

    # Parse main block
    nodelist = parser.parse(('elif', 'else', 'endvariant'))
    branches.append(_VariantBranch(experiment_name_var, variant_vars, nodelist))

    # Parse optional elif/else blocks.
    else_nodelist = None

    while True:
        token = parser.next_token()

        if token.contents.startswith('elif'):
            args = token.split_contents()
            args.pop(0)  # Skip 'elif'
            if not args:
                raise TemplateSyntaxError(
                    "'elif' requires at least one variant"
                )
            variant_vars = [template.Variable(b) for b in args]
            nodelist = parser.parse(('elif', 'else', 'endvariant'))
            branches.append(
                _VariantBranch(experiment_name_var, variant_vars, nodelist)
            )

        elif token.contents == 'else':
            else_nodelist = parser.parse(('endvariant',))
            parser.delete_first_token()
            break

        elif token.contents == 'endvariant':
            break

        else:
            raise TemplateSyntaxError(f'Unexpected tag: {token.contents}')

    return _VariantBlockNode(experiment_name_var, branches, else_nodelist)


class _SwitchNode(Node):
    def __init__(self, name, nodelist_on, nodelist_off):
        self.name = template.Variable(name)
        self.nodelist_on = nodelist_on
        self.nodelist_off = nodelist_off

    def render(self, context):
        request = context['request']
        name = self.name.resolve(context)
        nodelist = (
            self.nodelist_on if is_on(request, name) else self.nodelist_off
        )
        return nodelist.render(context) if nodelist is not None else ''


def _parse_switch_node(parser, token):
    try:
        tag_name, switch_name = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError(f'{tag_name} tag requires a switch name')

    end_tag_name = f'end{tag_name}'
    nodelist_first = parser.parse(('else', end_tag_name))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_second = parser.parse((end_tag_name,))
        parser.delete_first_token()
    else:
        nodelist_second = None

    return switch_name, nodelist_first, nodelist_second


@register.tag(name='switchon')
def switchon(parser, token):
    """
    Template tag that conditionally renders a block if a named switch is on.

    `switchon` is like an if/else that renders content conditionally based on
    the active variant of an experiment. switchon is similar to the `variant`
    tag, but with the implicit variant 'on' for the primary block and 'off' for
    the else block.

    To use `switchon` with an experiment, it should be configured as a switch:
        declare only `on` or `off`
    as variants.

    Example:

        {% switchon "super_cool_feature" %}
            Content displayed if the switch is on
        {% else %}
            Optional content displayed if the switch is off...
        {% endswitchon %}
    """
    switch_name, nodelist_on, nodelist_off = _parse_switch_node(parser, token)
    return _SwitchNode(switch_name, nodelist_on, nodelist_off)


@register.tag(name='switchoff')
def switchoff(parser, token):
    """
    Template tag that conditionally renders a block if a named switch is off.

    switchoff is like an if/else that renders content conditionally based on the
    active variant of an experiment. switchoff is similar to the `variant` tag,
    but with the implicit variant 'off' for the primary block and 'on' for the
    else block.

    To use `switchoff` with an experiment, it should declare only `on` or `off`
    as variants.

    Example:

        {% switchoff "super_cool_feature" %}
            Content displayed if the switch is off
        {% else %}
            Optional content displayed if the switch is on...
        {% endswitchoff %}
    """
    switch_name, nodelist_off, nodelist_on = _parse_switch_node(parser, token)
    return _SwitchNode(switch_name, nodelist_on, nodelist_off)


__all__ = [
    'variant',
    'switchon',
    'switchoff',
]
