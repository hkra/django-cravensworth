# Restrict overrides by IP address

Overrides are useful for testing or demoing functionality, but you don't want
just anyone to be able to override your experiments. You can restrict overriding
capability by IP address, so overrides will only take effect for requests
originating from allowed IP addresses.

Set the [ENABLED_IPS](../getting-started/configuration.md#enabled-ips) setting to a list of allowed IP addresses.

    'ENABLED_IPS': [
        '12.34.56.78',
        ...
    ]

If `ENABLED_IPS` is unset or `None`, IP address will not be checked, and anyone
can override. To disallow overriding for all IPs, set `ENABLED_IPS` to an empty
list.

!!! WARNING
    Experiments are not a mechanism for authentication or authorization. Nor is
    IP restriction to be considered a security measure.

IP restriction requires the remote address of the client. If your application is
behind a proxy or load balancer, ensure that it forwards the client IP address.
