from cravensworth.core.experiment import get_state
from cravensworth.core.utils import set_tracking_key


def cravensworth_middleware(get_response):
    """
    Middleware that extracts overrides from incoming requests and eagerly adds
    cravensworth data to the request.

    This should be added to the `MIDDLEWARE` list in your Django settings.
    """

    def middleware(request):
        get_state(request)
        response = get_response(request)
        set_tracking_key(request, response)
        return response

    return middleware
