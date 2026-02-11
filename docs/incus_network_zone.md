# incus_network_zone (Module)

Manage Incus network zones

Manage Incus network zones (create, delete, configure).

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `name` | True |  |  | Name of the network zone. |
| `state` | False | present | ['present', 'absent'] | State of the network zone. |
| `description` | False |  |  | Description of the network zone. |
| `config` | False |  |  | Dictionary of configuration options. |
| `project` | False | default |  | The project context. Defaults to 'default'. |
| `remote` | False | local |  | Remote Incus server. Defaults to 'local'. |

## Examples

```yaml
- name: Create a network zone
  crystian.incus.incus_network_zone:
    name: incus.test
    description: "Internal DNS zone"
    config:
      dns.domain: incus.test

- name: Delete a network zone
  crystian.incus.incus_network_zone:
    name: incus.test
    state: absent
```

## Return Values

```yaml
msg:
  description: Status message
  returned: always
  type: str
```
