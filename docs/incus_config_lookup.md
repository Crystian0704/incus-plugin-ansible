# incus_config (Lookup Plugin)

Get Incus instance configuration

This lookup returns the configuration of an Incus instance.
It wraps 'incus query /1.0/instances/<instance>'.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `remote` | False | local |  | The remote Incus server to query. Defaults to 'local'. |
| `project` | False | default |  | The project to query. Defaults to 'default'. |

## Examples

```yaml
- name: Get config for an instance
  debug:
    msg: "{{ lookup('crystian.incus.incus_config', 'my-container') }}"
```

## Return Values

```yaml
_raw:
    description: Instance configuration dictionary
    type: dict
```
