# Incus Export Module

The `incus_export` module allows you to export instances to backup files.

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `instance` / `name` | Yes | - | Name of the instance. |
| `path` / `dest` | Yes | - | Destination file path. |
| `compression` | No | - | Compression algo (gzip, bzip2, none, etc). |
| `optimized` | No | `false` | Use optimized storage format. |
| `instance_only` | No | `false` | Exclude snapshots. |
| `force` | No | `false` | Overwrite destination file. |

## Examples

### Export to tarball
```yaml
- name: Full backup
  crystian.incus.incus_export:
    instance: my-server
    dest: /backups/my-server-full.tar.gz
    force: true
```

### Export optimized
```yaml
- name: Optimized backup
  crystian.incus.incus_export:
    instance: my-server
    dest: /backups/my-server.bin
    optimized: true
```
