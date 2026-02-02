# Incus File Module

The `incus_file` module allows you to manage files inside Incus instances (containers and Virtual Machines). It is designed to mimic Ansible's standard `copy`, `fetch`, and `file` modules.

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` / `instance` | Yes | - | Name of the instance. |
| `state` | No | `pushed` | `pushed` (copy to), `pulled` (fetch from), `absent` (delete). |
| `src` | No | - | Source path. Local path for `pushed`; Remote path for `pulled`. |
| `dest` / `path` | No | - | Destination path. Remote path for `pushed`/`absent`; Local path for `pulled`. |
| `content` | No | - | String content to push (for `pushed`, mutually exclusive with `src`). |
| `owner` | No | - | Remote user name or ID (resolved via `incus exec id`). |
| `group` | No | - | Remote group name or ID. |
| `mode` | No | - | File permissions (e.g. `0644`). |
| `remote` | No | `local` | Remote server. |
| `project` | No | `default` | Project name. |

## Examples

### Push a local file (Copy Style)
```yaml
- name: Upload config file
  crystian.incus.incus_file:
    name: web-server
    src: files/nginx.conf
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    state: pushed
```

### Push content directly
```yaml
- name: Create hello file
  crystian.incus.incus_file:
    name: web-server
    content: "<html><body>Hello World</body></html>"
    dest: /var/www/html/index.html
    state: pushed
```

### Pull a file (Fetch Style)
```yaml
- name: Download logs
  crystian.incus.incus_file:
    name: web-server
    src: /var/log/nginx/access.log
    dest: /tmp/access.log
    state: pulled
```

### Delete a file (File Style)
```yaml
- name: Remove temporary file
  crystian.incus.incus_file:
    name: web-server
    dest: /tmp/garbage.txt
    state: absent
```
