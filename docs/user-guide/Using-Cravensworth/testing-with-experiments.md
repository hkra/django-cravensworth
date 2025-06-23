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

Experiments can be overriden for testing purposes in many ways, a few of which
are:

* Providing a local experiment source for tests using `@override_settings`.
* Changing the determined variant of the experiment under test using
  `@override_settings` (set the variant allocation to 100%).
* Override the determined variant by setting an override cookie.
* Setting a fake or mock state object on the test request.

Of these options, setting the override cookie is perhaps the least gross. You
can do that like this:

    def test_a_thing():
        self.client.cookies.load({'__cw': 'a_thing:active'})
        response = self.client.get('/')

        # Check the response...

# Cleanup

Having to override experiment bahavior can be _the worst_, so remember to clean
up your experiments when you are done with them.
