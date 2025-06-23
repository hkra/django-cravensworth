# Using experiments from JavaScript

Cravensworth does not currently have any prescribed method for accessing
experiments from JavaScript. Experiment state can be accessed from the request
using `get_state()`.

To make it available to the frontend, you could serialize it and write it to a
script block the page. Or you could make an API that the frontend calls to get
variants.
