# Populate a context

The default context only provides the Django user and a tracking key. That may
be enough to to implement some simple experiments, but if you want use more
advanced rules you will need to populate the context with whatever data your
rules require.

## Custom context providers

The middleware will load whatever context provider is configured in settings,
and will default to [DjangoRequestContextProvider][cravensworth.core.experiment.DjangoRequestContextProvider]
if no provider is configured.

To use a custom provider, create a class that extends the `ContextProvider` base
class. The middleware will pass the request context as a keyword argument.


    class MyContextProvider(DjangoRequestContextProvider):

        def context(self, **kwargs) -> Context:
            request = kwargs.pop('request')

            # Use the request to do stuff...or don't.

            return {
                # A dictionary with a all your stuff in it...
            }

Tell Cravensworth about your provider by setting the `CONTEXT_PROVIDER` setting
to the import string of your context provider class.

    CRAVENSWORTH = {
        'CONTEXT_PROVIDER': 'some.package.MyContextProvider',
        ...
    }
