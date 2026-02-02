# Incus Instance Module Examples

This document provides usage examples for the `incus_instance` module and their expected return values.

## 1. Create a Container (Stopped)
Equivalent to `incus init`.

```yaml
- name: Create a container (incus init)
  crystian.incus.incus_instance:
    name: my-container
    remote_image: images:debian/12
    started: false
  register: result
```

### Return Value
```json
{
    "changed": true,
    "instance": {
        "architecture": "x86_64",
        "config": {
            "image.architecture": "amd64",
            "image.description": "Debian 12 amd64 (20240101_12:00)",
            "image.os": "Debian",
            "image.release": "bookworm"
        },
        "created_at": "2024-01-01T12:00:00Z",
        "description": "",
        "devices": {
            "root": {
                "path": "/",
                "pool": "default",
                "type": "disk"
            }
        },
        "name": "my-container",
        "status": "Stopped",
        "status_code": 102,
        "type": "container"
    },
    "state": null
}
```

## 2. Launch a Container (Running)
Equivalent to `incus launch`.

```yaml
- name: Launch a container
  crystian.incus.incus_instance:
    name: my-running-container
    remote_image: images:alpine/edge
    started: true
  register: result
```

### Return Value
```json
{
    "changed": true,
    "instance": {
        "name": "my-running-container",
        "status": "Running",
        "status_code": 103,
        "type": "container",
        "..." : "..."
    },
    "state": {
        "cpu": {
            "usage": 123456789
        },
        "memory": {
            "usage": 1048576
        },
        "network": {
            "eth0": {
                "addresses": [
                    {
                        "address": "10.0.0.5",
                        "family": "inet",
                        "netmask": "24",
                        "scope": "global"
                    }
                ],
                "state": "up"
            }
        },
        "pid": 1234,
        "status": "Running"
    }
}
```

## 3. Remote Launch
Launch an instance on a remote server.

```yaml
- name: Launch on remote
  crystian.incus.incus_instance:
    name: ci-runner
    remote: kawa
    remote_image: images:debian/13
    started: true
  register: result
```

### Return Value
```json
{
    "changed": true,
    "instance": {
        "name": "ci-runner",
        "status": "Running",
        "location": "kawa",
        "..." : "..."
    },
    "state": {
        "status": "Running",
        "..." : "..."
    }
}
```

## 4. Complex Container Configuration
Launch a container with specific resource limits, network, and storage volume.
*Note: Storage volumes (e.g., `testvol`) must likely exist or be handled by the module depending on pool config.*

```yaml
- name: Complex Container
  crystian.incus.incus_instance:
    name: app-container
    remote_image: images:alpine/edge
    started: true
    description: "Production App"
    storage: default
    network: incusbr0
    config:
      limits.cpu: "2"
      limits.memory: "512MiB"
    devices:
      logvol:
        path: /var/log/app
        pool: default
        source: log-volume
        type: disk
```

### Return Value
```json
{
    "changed": true,
    "instance": {
        "name": "app-container",
        "config": {
            "limits.cpu": "2",
            "limits.memory": "512MiB",
            "..." : "..."
        },
        "devices": {
            "logvol": {
                "path": "/var/log/app",
                "pool": "default",
                "source": "log-volume",
                "type": "disk"
            },
            "root": {
                "path": "/",
                "pool": "default",
                "type": "disk"
            }
        },
        "description": "Production App",
        "status": "Running",
        "type": "container"
    }
}
```

## 5. Virtual Machine
Launch a Virtual Machine with secureboot disabled.

```yaml
- name: Launch VM
  crystian.incus.incus_instance:
    name: win-vm
    remote_image: images:windows/11
    vm: true
    started: true
    config:
      limits.cpu: "4"
      limits.memory: "8GiB"
      security.secureboot: "false"
```

### Return Value
```json
{
    "changed": true,
    "instance": {
        "name": "win-vm",
        "type": "virtual-machine",
        "status": "Running",
        "..." : "..."
    },
    "state": {
        "status": "Running",
        "..." : "..."
    }
}
```

## 6. Cloud-Init Configuration
Launch containers or VMs with cloud-init configuration.

### Basic User-Data
```yaml
- name: Web Server Container
  crystian.incus.incus_instance:
    name: web-01
    remote_image: images:ubuntu/22.04/cloud
    cloud_init_user_data: |
      #cloud-config
      package_upgrade: true
      packages:
        - nginx
        - git
    cloud_init_network_config: |
      version: 2
      ethernets:
        eth0:
          dhcp4: true
```

### VM with Cloud-Init Disk
For virtual machines that might not have the agent available immediately, attaching a config disk is recommended.

```yaml
- name: DB VM
  crystian.incus.incus_instance:
    name: db-01
    remote_image: images:debian/12/cloud
    vm: true
    cloud_init_disk: true
    cloud_init_user_data: "{{ lookup('file', 'cloud-init/db-server.yml') }}"

### File-based User Data (using Ansible lookup)
You can directly pass a file path content using Ansible `lookup`.

```yaml
- name: File-based User Data (using Ansible lookup)
  crystian.incus.incus_instance:
    name: file-test
    remote_image: images:alpine/edge/cloud
    cloud_init_user_data: "{{ lookup('file', '/path/to/my-config.yaml') }}"
```

### Complete Cloud-Init Example
Using `cloud_init_` prefixed parameters for clarity.

```yaml
- name: Full Config
  crystian.incus.incus_instance:
    name: full-ci-test
    remote_image: images:ubuntu/22.04/cloud
    cloud_init_user_data: |
      #cloud-config
      package_upgrade: true
    cloud_init_network_config: |
      version: 2
      ethernets:
        eth0:
          dhcp4: true
```
