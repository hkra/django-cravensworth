from django.urls import path, include
from django.views.generic import TemplateView

from .views import (
    fancy_model_view,
    named_redirect_view,
    on_page,
    off_page,
    home,
)

template_tag_test_urls = [
    path('/', home, name='home'),
    # Switchon
    path(
        'on-single/', TemplateView.as_view(template_name='switchon_single.html')
    ),
    path(
        'on-double/', TemplateView.as_view(template_name='switchon_double.html')
    ),
    path(
        'on-variable/',
        TemplateView.as_view(template_name='switchon_variable.html'),
    ),
    path(
        'on-content/',
        TemplateView.as_view(template_name='switchon_content.html'),
    ),
    # Switchoff
    path(
        'off-single/',
        TemplateView.as_view(template_name='switchoff_single.html'),
    ),
    path(
        'off-double/',
        TemplateView.as_view(template_name='switchoff_double.html'),
    ),
    path(
        'off-variable/',
        TemplateView.as_view(template_name='switchoff_variable.html'),
    ),
    path(
        'off-content/',
        TemplateView.as_view(template_name='switchoff_content.html'),
    ),
    path(
        'variant-single/',
        TemplateView.as_view(template_name='variant_single.html'),
    ),
    path(
        'variant-multiple/',
        TemplateView.as_view(template_name='variant_multiple.html'),
    ),
    path(
        'variant-else/',
        TemplateView.as_view(template_name='variant_else.html'),
    ),
    path(
        'variant-none/',
        TemplateView.as_view(template_name='variant_none.html'),
    ),
    path(
        'variant-unknown/',
        TemplateView.as_view(template_name='variant_unknown.html'),
    ),
    path(
        'variant-variable/',
        TemplateView.as_view(template_name='variant_variable.html'),
    ),
]

urlpatterns = [
    path('redirected/', named_redirect_view, name='view-redirect'),
    path('model-redirected/', fancy_model_view, name='model-view-redirect'),
    path('active/', on_page),
    path('inactive/', off_page),
    path('templates/', include(template_tag_test_urls)),
]
