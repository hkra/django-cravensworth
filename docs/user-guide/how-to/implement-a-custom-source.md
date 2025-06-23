# Implement a custom source

If you want to load experiments from a source not supported by Cravensworth's
provided sources, you can implement your own source.

## Creating your source

Custom sources can inherit from the [Source][cravensworth.core.source.Source]
base class.

`Source` has only one method to implement, `load()`, which returns an iterable
of [Experiment][cravensworth.core.experiment.Experiment]s. `load()` will be
called for every request when the middleware is installed. This is a crucial
detail for performance considerations, as discussed below.

### Performance considerations

Called on Every Request: As noted in the base class documentation, `load()` is
called for every request when `cravensworth_middleware` is in use.

Minimize Expensive Operations: Avoid performing time-consuming operations (e.g.,
complex database queries, external API calls with high latency) directly within
`load()` without proper caching.

Caching: For sources that involve I/O or computationally intensive tasks,
implementing a caching mechanism is highly recommended. You could cache the
loaded experiments for a period, invalidating the cache when underlying data
changes or after a timeout.

Consider how often your experiment data changes in the backend and how quickly
you want those changes to take effect. If experiments are frequently updated,
your caching strategy needs to reflect that to ensure users are seeing the most
up-to-date experiment assignments. If data staleness is acceptable for a short
period, a simpler time-based cache might suffice.

## Using your source

Set the [SOURCE](../getting-started/configuration.md#source) setting to the
import string of your source.
