# incus_config

Manage Incus instance configuration and devices.

## Synopsis

* Manage configuration options (e.g. `limits.memory`) and devices for Incus instances.
* This module complements `incus_instance` which is primarily for creation/state.
* Useful for modifying running instances or managing complex device setups.

## Parameters

| Parameter | Type | Required | Default | Choices | Description |
|---|---|---|---|---|---|
| name | str | yes | | | Name of the instance. |
| remote | str | no | | | Remote server to target. |
| state | str | no | present | present, absent | Desired state of the config/devices. |
| config | dict | no | | | Dictionary of configuration options. |
| devices | dict | no | | | Dictionary of devices to manage. |

## Examples

```yaml
- name: Set memory limit
  crystian.incus.incus_config:
    name: my-container
    config:
      limits.memory: 2GiB

- name: Add a network device
  crystian.incus.incus_config:
    name: my-container
    devices:
      eth1:
        type: nic
        nictype: bridged
        parent: incusbr0

- name: Update device MTU
  crystian.incus.incus_config:
    name: my-container
    devices:
      eth1:
        mtu: 1400

- name: Remove configuration
  crystian.incus.incus_config:
    name: my-container
    state: absent
    config:
      - limits.memory

- name: Remove device
  crystian.incus.incus_config:
    name: my-container
    state: absent
    devices:
      - eth1
```
