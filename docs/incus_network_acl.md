# incus_network_acl (Module)

Manage Incus network ACLs

Manage Incus network ACLs (create, delete, configure).

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `name` | True |  |  | Name of the ACL. |
| `state` | False | present | ['present', 'absent'] | State of the ACL. |
| `description` | False |  |  | Description of the ACL. |
| `egress` | False |  |  | List of egress rules. |
| `ingress` | False |  |  | List of ingress rules. |
| `config` | False |  |  | Dictionary of configuration options. |
| `force` | False | False |  | Force deletion of the ACL even if it is referenced by networks. Only used with state=absent. |
| `project` | False | default |  | The project context. Defaults to 'default'. |
| `remote` | False | local |  | Remote Incus server. Defaults to 'local'. |

## Examples

```yaml
- name: Create a network ACL
  crystian.incus.incus_network_acl:
    name: my-acl
    description: "My custom ACL"
    ingress:
      - action: allow
        protocol: tcp
        destination_port: 80
    egress:
      - action: allow
        protocol: tcp
        destination_port: 80
    config:
      user.mykey: myvalue

- name: Delete a network ACL
  crystian.incus.incus_network_acl:
    name: my-acl
    state: absent
```

## Return Values

```yaml
msg:
  description: Status message
  returned: always
  type: str
```
