from django.http import HttpResponse

from cravensworth.core.decorators import switch_on


def home(request):
    return HttpResponse('OK')


def fancy_model_view(request):
    return HttpResponse('OK')


def named_redirect_view(request):
    return HttpResponse('OK')


@switch_on('active')
def on_page(request):
    return HttpResponse('Active page')


@switch_on('inactive')
def off_page(request):
    return HttpResponse('Inactive page')
