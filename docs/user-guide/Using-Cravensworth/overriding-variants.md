# Overriding variants

There may be times when you wish to temporarily override determined variant of
an experiment.

For example, let's say you have an experiment the controls a new section on your
app's home page. You have three variants:

* `active` - Users see the new section.
* `inactive` Users don't see the new section.
* `control` Holdout groups; users will not see the new section.

You haven't begun roll-out yet, so the experiment is not active (i.e., inactive
is 100%). But you want to test (or demo) the new feature before rolling it out
to make sure it all looks good.

Another possible scenario is that you want to write some automated tests. That's
hard to do if the functionality changes because of an experiment.

In these cases, you can force Cravensworth to use whatever variant you desire
by overriding the determined variant with the one you want. This is done using
a cookie. By default, the cookie is called `__cw`, but you may choose any name
you want by setting the `OVERRIDE_COOKIE` config setting in your `settings.py`.

The value of the cookie is a space-delimited list of experiments and variants.
To override the `inactive_experiment` experiment and force the `active` variant
to be used, the value of the cookie should be `inactive_experiment:active`.

You can set this cookie on the client, in JavaScript, or on the server side.
It's up to you.
