# incus_list (Lookup Plugin)

List Incus instances

This lookup returns a list of Incus instances, similar to 'incus list'.
It returns a list of dictionaries, where each dictionary represents an instance.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `remote` | False | local |  | The remote Incus server to query. Defaults to 'local'. |
| `project` | False | default |  | The project to query. Defaults to 'default'. |
| `filters` | False |  |  | List of filters to apply (e.g. 'status=RUNNING', 'type=container'). |
| `all_projects` | False | False |  | If true, list instances from all projects. |

## Examples

```yaml
- name: List all running containers
  debug:
    msg: "{{ lookup('crystian.incus.incus_list', filters=['status=RUNNING', 'type=container']) }}"

- name: List all instances on a remote
  debug:
    msg: "{{ lookup('crystian.incus.incus_list', remote='myremote') }}"
```

## Return Values

```yaml
_list:
    description: List of instance dictionaries
    type: list
```
