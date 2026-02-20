# incus_info (Module)

Get Incus instance info and state

This module returns the full information of an Incus instance, including runtime state.
It combines 'incus query /1.0/instances/<instance>' and 'incus query /1.0/instances/<instance>/state'.
Useful for gathering facts about an instance on a remote host.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `name` | True |  |  | Name of the instance. |
| `remote` | False |  |  | The remote Incus server to query. Defaults to 'local'. |
| `project` | False | default |  | The project to query. Defaults to 'default'. |

## Examples

```yaml
- name: Get info for an instance
  crystian.incus.incus_info:
    name: my-container
  register: instance_info

- name: Debug info
  debug:
    var: instance_info.info
```

## Return Values

```yaml
info:
    description: Instance info dictionary (config + state)
    type: dict
    returned: always
```
