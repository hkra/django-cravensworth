from django.http import HttpResponse, Http404
from django.test import RequestFactory, SimpleTestCase

from cravensworth.core.experiment import (
    Context,
    set_state,
    Experiment,
    Audience,
    Allocation,
    CravensworthState,
)
from cravensworth.core.decorators import variant

from tests.testapp.models import FancyModel


class TestVariant(SimpleTestCase):
    def setUp(self):
        factory = RequestFactory()
        state = CravensworthState(
            experiments=[
                Experiment(
                    name='on_switch',
                    identity='random',
                    variants=('on', 'off'),
                    audiences=(
                        Audience(
                            rule=None,
                            allocations=(
                                Allocation(variant='on', percent=100),
                            ),
                        ),
                    ),
                ).validate(),
                Experiment(
                    name='off_switch',
                    identity='random',
                    variants=('on', 'off'),
                    audiences=(
                        Audience(
                            rule=None,
                            allocations=(
                                Allocation(variant='off', percent=100),
                            ),
                        ),
                    ),
                ).validate(),
                Experiment(
                    name='multivariant',
                    identity='random',
                    variants=('active', 'inactive', 'control'),
                    audiences=(
                        Audience(
                            rule=None,
                            allocations=(
                                Allocation(variant='active', percent=100),
                            ),
                        ),
                    ),
                ).validate(),
            ],
            overrides={},
            context=Context(),
        )
        self.request = factory.get('/')
        set_state(self.request, state)

    def test_renders_view_when_variant_matches(self):
        @variant('on_switch', 'on')
        def some_page(request):
            return HttpResponse('OK')

        response = some_page(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')

    def test_renders_view_when_variant_list_matches(self):
        @variant('multivariant', ['active', 'control'])
        def some_page(request):
            return HttpResponse('OK')

        response = some_page(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')

    def test_redirects_to_model_view_when_variant_does_not_match(self):
        @variant('off_switch', 'on', redirect_to=FancyModel)
        def some_page(request):
            return HttpResponse('OK')

        response = some_page(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('location'), '/model-redirected/')

    def test_redirects_to_model_view_when_variant_list_does_not_match(self):
        @variant(
            'multivariant', ['control', 'inactive'], redirect_to=FancyModel
        )
        def some_page(request):
            return HttpResponse('OK')

        response = some_page(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get('location'), '/model-redirected/')

    def test_redirects_to_named_view_when_variant_does_not_match(self):
        @variant('off_switch', 'on', redirect_to='view-redirect')
        def some_page(request):
            return HttpResponse('OK')

        response = some_page(self.request)
        assert response.status_code == 302
        assert response.headers.get('location') == '/redirected/'

    def test_redirects_to_url_when_variant_does_not_match(self):
        @variant('off_switch', 'on', redirect_to='https://www.example.com/')
        def some_page(request):
            return HttpResponse('OK')

        response = some_page(self.request)
        assert response.status_code == 302
        assert response.headers.get('location') == 'https://www.example.com/'

    def test_raises_404_when_no_redirect_provided(self):
        @variant('off_switch', 'on')
        def some_page(request):
            return HttpResponse('OK')

        with self.assertRaises(Http404):
            some_page(self.request)
