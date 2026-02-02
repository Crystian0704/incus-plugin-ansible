# Incus Publish Module

The `incus_publish` module allows you to create new images from existing instances or snapshots.

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `instance` | Yes | - | Source instance name. |
| `alias` | Yes | - | New image alias. |
| `snapshot` | No | - | Source snapshot name. |
| `public` | No | `false` | Make public. |
| `expire` | No | - | Expiry date. |
| `reuse` | No | `false` | Overwrite existing alias. |

## Examples

### Publish instance
```yaml
- name: Create template image
  crystian.incus.incus_publish:
    instance: web-server
    alias: web-server-v1
    public: true
```

### Publish snapshot
```yaml
- name: Create golden image from snapshot
  crystian.incus.incus_publish:
    instance: web-server
    snapshot: clean-state
    alias: golden-web
    reuse: true
```
