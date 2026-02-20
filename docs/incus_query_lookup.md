# incus_query (Lookup Plugin)

Query Incus API

This lookup performs a raw query against the Incus API.
Useful for retrieving information not covered by specific lookups.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `remote` | False | local |  | The remote Incus server to query. Defaults to 'local'. |
| `project` | False | default |  | The project to query. Defaults to 'default'. |

## Examples

```yaml
- name: Get project info
  debug:
    msg: "{{ lookup('crystian.incus.incus_query', '/1.0/projects/default') }}"
```

## Return Values

```yaml
_raw:
    description: API response (parsed JSON)
    type: dict
```
