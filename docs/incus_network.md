# incus_network (Module)

Manage Incus networks

Manage Incus networks (create, delete, configure).

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `name` | True |  |  | Name of the network. |
| `state` | False | present | ['present', 'absent'] | State of the network. |
| `type` | False | bridge |  | Type of the network (e.g., 'bridge', 'ovn', 'macvlan', 'sriov'). Only used during creation. |
| `description` | False |  |  | Description of the network. |
| `config` | False |  |  | Dictionary of configuration options (e.g., 'ipv4.address': '10.0.0.1/24'). |
| `project` | False | default |  | The project context. Defaults to 'default'. |
| `target` | False |  |  | Cluster member target. |

## Examples

```yaml
- name: Create a bridge network
  crystian.incus.incus_network:
    name: incusbr0
    type: bridge
    description: "My bridge network"
    config:
      ipv4.address: 10.0.0.1/24
      ipv4.nat: true
      ipv6.address: none

- name: Create an OVN network
  crystian.incus.incus_network:
    name: ovn-net
    type: ovn
    config:
      network: incusbr0

- name: Delete a network
  crystian.incus.incus_network:
    name: incusbr0
    state: absent
```

## Return Values

```yaml
msg:
  description: Status message
  returned: always
  type: str
```
