from django.http import HttpResponse
from django.views.generic import TemplateView

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


# Template tag test views
switchon_single_view = TemplateView.as_view(
    template_name='switchon_single.html'
)
switchon_double_view = TemplateView.as_view(
    template_name='switchon_double.html'
)
switchon_variable_view = TemplateView.as_view(
    template_name='switchon_variable.html'
)
switchon_content_view = TemplateView.as_view(
    template_name='switchon_content.html'
)

switchoff_single_view = TemplateView.as_view(
    template_name='switchoff_single.html'
)
switchoff_double_view = TemplateView.as_view(
    template_name='switchoff_double.html'
)
switchoff_variable_view = TemplateView.as_view(
    template_name='switchoff_variable.html'
)
switchoff_content_view = TemplateView.as_view(
    template_name='switchoff_content.html'
)

variant_single_view = TemplateView.as_view(template_name='variant_single.html')
variant_multiple_view = TemplateView.as_view(
    template_name='variant_multiple.html'
)
variant_else_view = TemplateView.as_view(template_name='variant_else.html')
variant_none_view = TemplateView.as_view(template_name='variant_none.html')
variant_unknown_view = TemplateView.as_view(
    template_name='variant_unknown.html'
)
variant_variable_view = TemplateView.as_view(
    template_name='variant_variable.html'
)
