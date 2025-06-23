# Experiments in code

## In a request-response context

Using experiments in an environment where a request is available is the default
assumed mode. Little is required to use experiments in your Django code.

Anywhere you have access to a `HttpRequest` object, you can call `is_variant()`,
`is_on()`, or `is_off`.

    from django.shortcuts import render
    from cravensworth.core import experiment


    def my_experimental_view(request):
        is_active = experiment.is_variant(request, 'my_experiment', 'active')
        feature_on = experiment.is_on(request, 'my_feature')

        context = {
            'experiment_is_active': is_active,
            'feature_is_on: feature_on,
        }
        return render(request, 'some_template.html', context)

The `decorators` package also provides some convenient decorators that you can
use to control access to views based on experiments or switches.

    from cravensworth.core.decorators import variant, switch_on


    @variant('my_experiment, 'active', redirect_to='/')
    def active_only_view(request):
        """This view can only be accessed if the variant is 'active'. If it is
        another variant, the user will be redirected to '/'
        """
        return render(request, 'experimental_template.html')


    @switch_on('best_new_feature')
    def switch_on_view(request):
        """This view can only be accessed if the switch is on. If it is off, the
        user will receive a 404 Not Found.
        """
        return render(request, 'new_feature_template.html')


## In a non-request context

If you don't have a request available, you can still use Cravensworth, but you
will have to do more of the setup work. Not having a request is common if you
are building command or a background job.

### Setting up the context

You can use the context provider, configured in `settings.py`, by calling
`get_context_provider()`, which returns an instance of a context provider.

    from cravensworth.core.experiment import get_context_provider

    context_provider = get_context_provider()
    context = context_provider.context(
        # Params as required by provider...
    )

!!! NOTE
    The default context provider is `DjangoRequestContextProvider`, which
    requires a request. To use context providers in a non-request context, you
    must configure a provider that doesn't require a request by setting the
    `CONTEXT_PROVIDER` setting in `settings.py`.

Or you can create a context directly by passing a dictionary to `Context()`
populated with data required for your experiments.

    from cravensworth.core.experiment import Context

    context = Context({
        # Data required by your experiments...
    })

### Overrides

If you want to use overrides variant in a non-request environment, you will need
to source them yourself. Overrides are provided to the state as a dictionary
mapping experiment name to the override variant.

### Loading experiments

To load experiments, you can call `get_source()` to get an instance of the
configured experiment source, then call `load()` to get the list of experiments.

Depending on your needs, you may only have to do this once. If you are using
experiments in a long-running process, where experiment updates need to go into
effect quickly, then you may have to call `load()` more often.

### Checking variants

Finally, we can put it all together to populate a state object and check
variants.

    from cravensworth.core.experiment import Context, CravensworthState
    from cravensworth.core.source import get_source

    import User from .models

    def some_batch_job_or_whatever():
        experiments = get_source().load()
        overrides = { 'my_super_experiment': 'active' }

        for user in User.objects.all():
            context = Context({'user': user})
            state = CravensworthState(experiments, overrides, context)

            if state.is_variant('my_super_experiment', 'active'):
                ... # Do something when variant is "active"...
            else:
                ... # Do something else...
