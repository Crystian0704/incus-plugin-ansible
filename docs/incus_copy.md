# incus_copy (Module)

Copy or move Incus instances

Copy or move Incus instances within or between servers.
Supports local and cross-server operations.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `source` | True |  |  | Source instance name (or remote:name for cross-server). |
| `dest` | True |  |  | Destination instance name (or remote:name for cross-server). |
| `move` | False | False |  | If true, move the instance instead of copying. The source instance will be deleted after transfer. |
| `instance_only` | False | False |  | Copy/move the instance without its snapshots. |
| `mode` | False | pull | ['pull', 'push', 'relay'] | Transfer mode for cross-server operations. |
| `storage` | False |  |  | Target storage pool for the copied/moved instance. |
| `profiles` | False |  |  | List of profiles to apply to the new instance. |
| `no_profiles` | False | False |  | Create the instance with no profiles applied. |
| `ephemeral` | False | False |  | Make the copied instance ephemeral. |
| `project` | False | default |  | Project to use. |
| `remote` | False | local |  | Remote server context (applied to both source and dest if they don't contain a colon). |

## Examples

```yaml
- name: Copy an instance locally
  crystian.incus.incus_copy:
    source: my-instance
    dest: my-instance-copy

- name: Move an instance (rename)
  crystian.incus.incus_copy:
    source: old-name
    dest: new-name
    move: true

- name: Copy without snapshots
  crystian.incus.incus_copy:
    source: my-instance
    dest: my-instance-copy
    instance_only: true

- name: Copy to a different storage pool
  crystian.incus.incus_copy:
    source: my-instance
    dest: my-instance-copy
    storage: fast-pool

- name: Copy across servers
  crystian.incus.incus_copy:
    source: local:my-instance
    dest: remote-server:my-instance
```

## Return Values

```yaml
msg:
  description: Status message
  returned: always
  type: str
```
