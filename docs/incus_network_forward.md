# incus_network_forward (Module)

Manage Incus network forwards

Manage Incus network forwards (create, delete, configure, port mapping).

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `network` | True |  |  | Name of the network. |
| `listen_address` | True |  |  | The listen IP address for the forward. |
| `state` | False | present | ['present', 'absent'] | State of the network forward. |
| `description` | False |  |  | Description of the network forward. |
| `config` | False |  |  | Dictionary of configuration options (e.g. target_address). |
| `ports` | False |  |  | List of port specifications. |
| `project` | False | default |  | The project context. Defaults to 'default'. |
| `remote` | False | local |  | Remote Incus server. Defaults to 'local'. |

## Examples

```yaml
- name: Create a network forward
  crystian.incus.incus_network_forward:
    network: mynetwork
    listen_address: 192.168.1.50
    description: "Web server forward"
    config:
      target_address: 10.0.0.10
    ports:
      - protocol: tcp
        listen_port: "80"
        target_address: 10.0.0.10
        target_port: "80"
      - protocol: tcp
        listen_port: "443"
        target_address: 10.0.0.10
        target_port: "443"

- name: Delete a network forward
  crystian.incus.incus_network_forward:
    network: mynetwork
    listen_address: 192.168.1.50
    state: absent
```

## Return Values

```yaml
msg:
  description: Status message
  returned: always
  type: str
```
