from django.urls import path, include

from .views import (
    fancy_model_view,
    named_redirect_view,
    on_page,
    off_page,
    home,
    switchon_single_view,
    switchon_double_view,
    switchon_variable_view,
    switchon_content_view,
    switchoff_single_view,
    switchoff_double_view,
    switchoff_variable_view,
    switchoff_content_view,
    variant_single_view,
    variant_multiple_view,
    variant_else_view,
    variant_none_view,
    variant_unknown_view,
    variant_variable_view,
)

template_tag_test_urls = [
    path('/', home, name='home'),
    # Switchon
    path('on-single/', switchon_single_view),
    path('on-double/', switchon_double_view),
    path('on-variable/', switchon_variable_view),
    path('on-content/', switchon_content_view),
    # Switchoff
    path('off-single/', switchoff_single_view),
    path('off-double/', switchoff_double_view),
    path('off-variable/', switchoff_variable_view),
    path('off-content/', switchoff_content_view),
    path('variant-single/', variant_single_view),
    path('variant-multiple/', variant_multiple_view),
    path('variant-else/', variant_else_view),
    path('variant-none/', variant_none_view),
    path('variant-unknown/', variant_unknown_view),
    path('variant-variable/', variant_variable_view),
]

urlpatterns = [
    path('redirected/', named_redirect_view, name='view-redirect'),
    path('model-redirected/', fancy_model_view, name='model-view-redirect'),
    path('active/', on_page),
    path('inactive/', off_page),
    path('templates/', include(template_tag_test_urls)),
]
