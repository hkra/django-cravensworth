from cravensworth.core.experiment import (
    get_context_provider,
    set_state,
    CravensworthState,
    extract_overrides,
)
from cravensworth.core.source import get_source
from cravensworth.core.utils import set_tracking_key


def cravensworth_middleware(get_response):
    """
    Middleware that extracts overrides from incoming requests and adds
    cravensworth data to the request.

    This should be added to the `MIDDLEWARE` list in your Django settings.
    """
    source = get_source()
    context_provider = get_context_provider()

    def middleware(request):
        overrides = extract_overrides(request)
        context = context_provider.context(request=request)
        experiments = source.load()
        state = CravensworthState(experiments, overrides, context)
        set_state(request, state)
        response = get_response(request)
        set_tracking_key(request, response)
        return response

    return middleware
