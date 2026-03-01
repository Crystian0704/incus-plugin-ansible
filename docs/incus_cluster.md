# incus_cluster (Module)

Manage Incus clusters

Enable clustering on a standalone server.
Generate join tokens for new members.
List and show cluster members.
Configure cluster member settings.
Manage cluster groups (create, assign, delete, list).
Remove members from the cluster.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `name` | False |  |  | Name of the cluster member. Required for C(state=enabled), C(state=present), C(state=absent). Not required for C(state=listed). |
| `state` | False | present | ['enabled', 'present', 'absent', 'listed'] | Desired state of the cluster member or operation. C(enabled) enables clustering on a standalone server, turning it into the first member. C(present) generates a join token for a new member to join the cluster. C(absent) removes a member from the cluster. C(listed) lists all cluster members (returns member list in C(members)). |
| `config` | False |  |  | Dictionary of configuration options to set on the cluster member. Uses C(incus cluster set <member> key=value). Only used with C(state=present) when the member already exists. |
| `groups` | False |  |  | Manage cluster groups. When C(state=present): a list of dicts with C(name) and optional C(description) creates groups. When C(state=present) and C(name) is set: a list of strings assigns groups to the member. When C(state=absent): a list of strings deletes groups. When C(state=listed) and C(groups=true): lists all cluster groups. |
| `force` | False | False |  | Force removal of a degraded member. Only used with C(state=absent). |
| `remote` | False | local |  | The remote Incus server to target. Defaults to 'local'. |
| `project` | False |  |  | The project context. |

## Examples

```yaml
- name: Enable clustering on a standalone server
  crystian.incus.incus_cluster:
    name: node1
    state: enabled

- name: Generate a join token for a new member
  crystian.incus.incus_cluster:
    name: node2
    state: present
  register: join_result

- name: Show join token
  debug:
    msg: "Join token: {{ join_result.token }}"

- name: List cluster members
  crystian.incus.incus_cluster:
    state: listed
  register: cluster_info

- name: Set cluster member config
  crystian.incus.incus_cluster:
    name: node1
    config:
      scheduler.instance: all
    state: present

- name: Create cluster groups
  crystian.incus.incus_cluster:
    groups:
      - name: compute
        description: "Compute nodes"
      - name: storage
        description: "Storage nodes"
    state: present

- name: Assign groups to a member
  crystian.incus.incus_cluster:
    name: node1
    groups:
      - compute
      - storage
    state: present

- name: List cluster groups
  crystian.incus.incus_cluster:
    groups: true
    state: listed

- name: Delete cluster groups
  crystian.incus.incus_cluster:
    groups:
      - compute
    state: absent

- name: Remove a member from the cluster
  crystian.incus.incus_cluster:
    name: node3
    state: absent
    force: true
```

## Return Values

```yaml
msg:
  description: Status message.
  returned: always
  type: str
token:
  description: Join token generated for a new member.
  returned: when state=present and a join token is generated
  type: str
members:
  description: List of cluster members.
  returned: when state=listed and groups is not set
  type: list
groups:
  description: List of cluster groups.
  returned: when state=listed and groups=true
  type: list
member:
  description: Details of a specific cluster member.
  returned: when state=present and member already exists
  type: dict
```
