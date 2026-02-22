# Testing with experiments

## Automated tests

When using experiments, the behavior of your application may not be
deterministic. Furthermore, the behavior of your test may change over time as
the configuration of your experiment changes. This can be a problem if you have
automated end-to-end tests.

Before running your tests, set the behavior you want by
[overriding experiment variants](overriding-variants.md) using the override
cookie. This will make sure that the code under test behaves the same way for
every test run.

## Django unit/integration tests

Experiments generally behave as expected in tests and should not require special
configuration if your test configuration is similar to your real project setup.
However, this may not be desirable in tests, where determinism is desired.

Experiments can be overriden for testing purposes in several ways.

### @override_settings

In a standard Django test case, `@override_settings` can be used to override the
`EXPERIMENT` configuration. For example, if you are using a switch called
"switch" and you want to make sure it is on for your test, override your test
config so the switch is on:

```python
class MyThingTest(SimpleTestCase):

    @override_settings(CRAVENSWORTH={'EXPERIMENTS': ['switch:on']})
    def test_my_thing(self):
        ...
```

`@override_settings` can be used to override other parts of the configuration,
too. So you could also create a `Source` just for tests, override the `SOURCE`
import string to point at your test source.

### Set an override cookie

Another way is to utilize the override mechanism by setting a cookie on the
request object. The [cravensworth.core.testing](../../api-reference/testing.md)
package provides a utility that can be used in tests.

```python
from cravensworth.core.testing import override_experiment

class MyThingTest(SimpleTestCase):
    factory = RequestFactory()

    def test_my_thing(self):
        request = self.factory.get('/my/switchy/path')
        override_experiment(request, 'switch', 'on')
        ...

    def test_multiple_things(self):
        request = self.factory.get('/my/super/switchy/path')
        override_experiment(request, {
            'switch1': 'on',
            'switch2': 'off',
        })
        ...
```

# Cleanup

Having to override experiment bahavior in tests can be annoying, so remember to
clean up your experiments when you are done with them.
