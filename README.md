# Ansible Collection - crystian.incus

Ansible Collection for managing Incus containers and virtual machines.

## Requirements

This collection requires the `incus` client to be installed on the Ansible control node (where you run the playbook).

- **Incus Client**: `incus` or `incus-client` package must be installed and available in the PATH.
- **Python**: 3.6+

### Tested Configuration
The collection was developed and validated in the following environment:
- **Host OS**: Debian 12
- **Incus Server/Client**: 6.21
- **Ansible**: 13.3.0
- **Ansible Core**: 2.20.2

## Installation

### From Ansible Galaxy (Not yet published)
```bash
ansible-galaxy collection install crystian.incus
```

### From Git
```bash
ansible-galaxy collection install git+https://github.com/Crystian0704/incus-plugin-ansible.git
```

### Local Build
```bash
ansible-galaxy collection build
ansible-galaxy collection install crystian-incus-1.0.0.tar.gz
```

## Modules

| Module | Description |
|---|---|
| `incus_instance` | Create, manage, and delete Incus instances (containers/VMs). |
| `incus_storage` | Manage Incus storage pools. |
| `incus_storage_volume` | Manage Incus storage volumes. |
| `incus_profile` | Manage Incus profiles. |
| `incus_project` | Manage Incus projects. |
| `incus_image` | Manage Incus images. |
| `incus_remote` | Manage Incus remotes. |
| `incus_exec` | Execute commands in instances. |
| `incus_file` | Manage files in instances. |
| `incus_snapshot` | Manage instance snapshots. |
| `incus_network` | Manage Incus networks. |
| `incus_network_acl` | Manage Incus network ACLs. |
| `incus_network_zone` | Manage Incus network zones. |
| `incus_network_forward` | Manage Incus network forwards. |
| `incus_info` | Get information about Incus resources. |
| `incus_admin_init` | Initialize Incus server. |
| `incus_config` | Manage instance configuration and devices. |
| `incus_export` | Export instance backups. |
| `incus_list` | List instances (module version). |
| `incus_publish` | Publish instances as images. |

## Lookup Plugins

| Lookup | Description |
|---|---|
| `incus_config` | Get configuration of an instance. |
| `incus_list` | List instances with filters. |
| `incus_info` | Get detailed info/state of an instance or server. |
| `incus_query` | Perform raw API queries. |

## Inventory Plugin

The collection includes a dynamic inventory plugin to query Incus instances.

| Plugin | Description |
|---|---|
| `incus_inventory` | Dynamic inventory from Incus instances. |

### Configuration Example
Create a file named `incus_inventory.yml`:

```yaml
plugin: crystian.incus.incus_inventory
remotes:
  - local
projects:
  - default
keyed_groups:
  - prefix: tag
    key: incus_user_tags
```

### Usage
```bash
ansible-inventory -i incus_inventory.yml --graph
```

For more details and advanced usage (grouping by OS, custom variables), see [Inventory Plugin Documentation](docs/incus_inventory.md).

## Usage Examples

### Create a Container
```yaml
- name: Create a Debian container
  crystian.incus.incus_instance:
    name: my-container
    remote_image: images:debian/12
    state: present
    tags:
      env: prod
      app: web
      owner: team-a
    started: true
```

### Create a Virtual Machine
```yaml
- name: Create a Debian VM
  crystian.incus.incus_instance:
    name: my-vm
    remote_image: images:debian/12
    vm: true
    config:
      limits.cpu: 2
      limits.memory: 2GiB
    state: present
```

### Create Instance with Cloud-Init
```yaml
- name: Create a web server
  crystian.incus.incus_instance:
    name: my-web-server
    remote_image: images:ubuntu/22.04/cloud
    started: true
    cloud_init_user_data: |
      #cloud-config
      package_upgrade: true
      packages:
        - nginx
    cloud_init_network_config: |
      version: 2
      ethernets:
        eth0:
          dhcp4: true
```

### Execute Command
```yaml
- name: Upgrade packages
  crystian.incus.incus_exec:
    instance_name: my-container
    command: apt-get update && apt-get upgrade -y
```

### Configure Instance
```yaml
- name: Set memory limit
  crystian.incus.incus_config:
    instance_name: my-container
    config:
      limits.memory: 4GiB
    tags:
      maintenance: "true"

```

### Manage Files
```yaml
- name: Push a file
  crystian.incus.incus_file:
    instance_name: my-container
    src: /local/path/file.txt
    dest: /remote/path/file.txt
    state: pushed
```

### Snapshot Management
```yaml
- name: Create a snapshot
  crystian.incus.incus_snapshot:
    instance_name: my-container
    snapshot_name: backup-snap
    state: present
```

### Network Management
```yaml
- name: Create a network
  crystian.incus.incus_network:
    name: my-network
    type: bridge
    config:
      ipv4.address: 10.0.1.1/24
      ipv4.nat: true
```

### Initialize Server (Preseed)
```yaml
- name: Init Incus
  crystian.incus.incus_admin_init:
    config:
      networks:
        - name: incusbr0
          type: bridge
          config:
            ipv4.address: auto
            ipv6.address: auto
      storage_pools:
        - name: default
          driver: dir
      profiles:
        - name: default
          devices:
            root:
              path: /
              pool: default
              type: disk
            eth0:
              name: eth0
              network: incusbr0
              type: nic
```

### Trust Management
```yaml
- name: Add client trust
  crystian.incus.incus_config:
    trust:
      name: my-ansible-client
    state: present
  register: trust_result

- name: Show token
  debug:
    msg: "Certificate added. Token: {{ trust_result.token }}"
```

### Lookup Plugin Usage
```yaml
- name: Get instance config
  debug:
    msg: "{{ lookup('crystian.incus.incus_config', 'my-container') }}"

- name: List running containers
  debug:
    msg: "{{ lookup('crystian.incus.incus_list', filters=['status=RUNNING', 'type=container']) }}"
```

## Running Tests

Integration tests are included to validate the functionality of the collection.

### Prerequisites
- Incus server running and configured on the local machine (`incus admin init`).
- `incus` client available in PATH.
- Permissions to manage incus (membership in `incus`).

### Running Integration Suite
Run the full integration test suite using `ansible-playbook`:

```bash
ansible-playbook tests/integration.yml
```

You can also run specific module tests using tags:
```bash
# Test only incus_instance module
ansible-playbook tests/integration.yml --tags incus_instance

# Force infrastructure recreation
ansible-playbook tests/integration.yml -e delete_infra=true
```

## Known Limitations

- **Missing Modules**: `incus_cluster` for `incus cluster` is not yet implemented.
- **Storage Backends**: Support for some specific storage backends is incomplete.
- **Testing**: More complex integration tests and edge cases need to be covered.

## Disclaimer

> [!WARNING]
> This collection was built with the assistance of **Google Antigravity** and **Gemini 3 Pro**.
> **Sandbox Validation Required**: All usage must be validated in a sandbox/test environment before production use.

## License
MIT
