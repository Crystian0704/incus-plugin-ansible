# Incus Snapshot Module

The `incus_snapshot` module allows you to manage instance snapshots.

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `instance` / `name` | Yes | - | Name of the instance. |
| `snapshot` / `snapshot_name` | Yes | - | Name of the snapshot. |
| `state` | No | `present` | `present`, `absent`, `restored`, `renamed`. |
| `new_name` | No | - | New name for snapshot (for `renamed`). |
| `expires` | No | - | Expiry date (e.g. `30d`, `2024-01-01`). Use at creation. |
| `reuse` | No | `false` | Overwrite existing snapshot. |
| `stateful` | No | `false` | Create stateful snapshot. |
| `cron` | No | - | `snapshots.schedule`. |
| `cron_stopped` | No | - | `snapshots.schedule.stopped`. |
| `pattern` | No | - | `snapshots.pattern`. |
| `expiry` | No | - | `snapshots.expiry`. |

## Examples

### Configure automated snapshots
```yaml
- name: Enable daily snapshots
  crystian.incus.incus_snapshot:
    instance: my-container
    cron: "@daily"
    expiry: "30d"
    cron_stopped: true
    pattern: "daily-%d"
```

### Create a snapshot
```yaml
- name: Backup container
  crystian.incus.incus_snapshot:
    instance: my-db
    snapshot: daily-backup
    state: present
    reuse: true
    expires: 7d
```

### Restore a snapshot
```yaml
- name: Restore backup
  crystian.incus.incus_snapshot:
    instance: my-db
    snapshot: daily-backup
    state: restored
```

### Delete a snapshot
```yaml
- name: Remove old backup
  crystian.incus.incus_snapshot:
    instance: my-db
    snapshot: daily-backup
    state: absent
```
