# incus_info (Lookup Plugin)

Get Incus instance info and state

This lookup returns the full information of an Incus instance, including runtime state.
It combines 'incus query /1.0/instances/<instance>' and 'incus query /1.0/instances/<instance>/state'.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `remote` | False | local |  | The remote Incus server to query. Defaults to 'local'. |
| `project` | False | default |  | The project to query. Defaults to 'default'. |

## Examples

```yaml
- name: Get info for an instance
  debug:
    msg: "{{ lookup('crystian.incus.incus_info', 'my-container') }}"
```

## Return Values

```yaml
_raw:
    description: Instance info dictionary (config + state)
    type: dict
```
