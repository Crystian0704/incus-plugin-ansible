# Incus Image Module

The `incus_image` module allows you to manage images in the Incus image store.

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `alias` | Yes | - | Alias of the image. |
| `state` | No | `present` | `present`, `absent`, `exported`. |
| `source` | No | - | Source remote/file (e.g. `images:alpine/3.18`). |
| `fingerprint` | No | - | Expected fingerprint. |
| `dest` | No | - | Destination for export. |
| `public` | No | `false` | Make public. |
| `auto_update` | No | `false` | Auto update copy. |

## Examples

### Copy remote image
```yaml
- name: Cache Alpine
  crystian.incus.incus_image:
    alias: alpine-edge
    source: images:alpine/edge
    state: present
    auto_update: true
```

### Import from file
```yaml
- name: Import backup
  crystian.incus.incus_image:
    alias: restored-image
    source: /tmp/backup.tar.gz
    state: present
```

### Export image
```yaml
- name: Export image
  crystian.incus.incus_image:
    alias: alpine-edge
    dest: /tmp/alpine-edge.tar.gz
    state: exported
```
