# Incus List Module Examples

This document provides usage examples for the `incus_list` module and their expected return values.

## 1. List All Local Instances
Retrieves a list of all instances on the local server.

```yaml
- name: List all local instances
  crystian.incus.incus_list:
  register: result
```

### Return Value
```json
{
    "changed": false,
    "list": [
        {
            "name": "my-container",
            "status": "Running",
            "type": "container",
            "architecture": "x86_64",
            "config": { ... },
            "devices": { ... },
            "state": { ... }
        },
        {
            "name": "stopped-vm",
            "status": "Stopped",
            "type": "virtual-machine",
            ...
        }
    ]
}
```

## 2. Filter by Status and Type
List only running containers.

```yaml
- name: List running containers
  crystian.incus.incus_list:
    filters:
      - status=Running
      - type=container
  register: result
```

### Return Value
```json
{
    "changed": false,
    "list": [
        {
            "name": "web-01",
            "status": "Running",
            "type": "container",
            ...
        }
    ]
}
```

## 3. List Remote Instances
List instances from a remote server (e.g., `kawa`).

```yaml
- name: List remote instances
  crystian.incus.incus_list:
    remote: kawa
  register: result
```

### Return Value
```json
{
    "changed": false,
    "list": [
        {
            "name": "remote-ct",
            "location": "kawa",
            "status": "Running",
            ...
        }
    ]
}
```

## 4. List All Remotes
List instances from **all** configured remotes (protocol `incus`), aggregating the results.

```yaml
- name: List instances from all remotes
  crystian.incus.incus_list:
    all_remotes: true
  register: result
```

### Return Value
```json
{
    "changed": false,
    "list": [
        {
            "name": "local-ct",
            "location": "local",
            "status": "Running",
            ...
        },
        {
            "name": "remote-ct",
            "location": "kawa",
            "status": "Running",
            ...
        }
    ]
}
```

## 5. List All Projects
List instances from all projects, not just the default one.

```yaml
- name: List all projects
  crystian.incus.incus_list:
    all_projects: true
  register: result
```
*Note: If `all_projects` is true, the `project` parameter is ignored.*

### Return Value
```json
{
    "changed": false,
    "list": [
        {
            "name": "dev-db",
            "project": "development",
            ...
        },
        {
            "name": "prod-db",
            "project": "production",
            ...
        }
    ]
}
```
