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
| [`incus_instance`](docs/incus_instance.md) | Create, manage, and delete Incus instances (containers/VMs). |
| [`incus_storage`](docs/incus_storage.md) | Manage Incus storage pools. |
| [`incus_storage_volume`](docs/incus_storage_volume.md) | Manage Incus storage volumes. |
| [`incus_profile`](docs/incus_profile.md) | Manage Incus profiles. |
| [`incus_project`](docs/incus_project.md) | Manage Incus projects. |
| [`incus_image`](docs/incus_image.md) | Manage Incus images (copy, import, export, delete, properties). |
| [`incus_remote`](docs/incus_remote.md) | Manage Incus remotes. |
| [`incus_copy`](docs/incus_copy.md) | Copy or move Incus instances. |
| [`incus_exec`](docs/incus_exec.md) | Execute commands in instances. |
| [`incus_file`](docs/incus_file.md) | Manage files in instances. |
| [`incus_snapshot`](docs/incus_snapshot.md) | Manage instance snapshots. |
| [`incus_network`](docs/incus_network.md) | Manage Incus networks. |
| [`incus_network_acl`](docs/incus_network_acl.md) | Manage Incus network ACLs. |
| [`incus_network_zone`](docs/incus_network_zone.md) | Manage Incus network zones. |
| [`incus_network_forward`](docs/incus_network_forward.md) | Manage Incus network forwards. |
| [`incus_info`](docs/incus_info.md) | Get information about Incus resources. |
| [`incus_admin_init`](docs/incus_admin_init.md) | Initialize Incus server. |
| [`incus_config`](docs/incus_config.md) | Manage instance configuration and devices. |
| [`incus_export`](docs/incus_export.md) | Export instance backups. |
| [`incus_list`](docs/incus_list.md) | List instances (module version). |
| [`incus_publish`](docs/incus_publish.md) | Publish instances as images. |

## Lookup Plugins

| Lookup | Description |
|---|---|
| [`incus_config`](docs/incus_config_lookup.md) | Get configuration of an instance. |
| [`incus_list`](docs/incus_list_lookup.md) | List instances with filters. |
| [`incus_info`](docs/incus_info_lookup.md) | Get detailed info/state of an instance or server. |
| [`incus_query`](docs/incus_query_lookup.md) | Perform raw API queries. |

## Inventory Plugin

The collection includes a dynamic inventory plugin that automatically discovers Incus instances and makes them available as Ansible hosts — **no need to maintain static inventory files manually**.

The plugin:
- Queries all configured remotes and projects for running instances.
- Creates **automatic groups** by remote (`incus_remote_local`), project (`incus_project_default`), and tags (`tag_env_prod`).
- Sets `ansible_connection: community.general.incus` so Ansible connects directly to containers/VMs via Incus.
- Exposes all `user.*` config keys as host variables for flexible grouping and filtering.

| Plugin | Description |
|---|---|
| [`incus_inventory`](docs/incus_inventory.md) | Dynamic inventory from Incus instances. |

### Quick Start

1. Create `incus_inventory.yml`:
```yaml
plugin: crystian.incus.incus_inventory
keyed_groups:
  - prefix: tag
    key: incus_user_tags
```

2. Enable the plugin in `ansible.cfg`:
```ini
[defaults]
inventory = incus_inventory.yml

[inventory]
enable_plugins = crystian.incus.incus_inventory, yaml
```

3. Verify:
```bash
ansible-inventory --graph
```

> [!NOTE]
> The inventory file **must** be named `*incus_inventory.yml` or `*incus_inventory.yaml`.

### Auto-Generated Groups

When your instances have tags (set via `incus_instance` or `incus_config`), the plugin creates groups automatically:

```yaml
# Instance created with:
- crystian.incus.incus_instance:
    name: web-01
    remote_image: images:debian/12
    tags:
      env: prod
      role: webserver
      team: platform
```

Results in the following inventory groups:
```
@all:
  |--@incus_remote_local:
  |  |--web-01
  |--@incus_project_default:
  |  |--web-01
  |--@tag_env_prod:
  |  |--web-01
  |--@tag_role_webserver:
  |  |--web-01
  |--@tag_team_platform:
  |  |--web-01
```

### Filter by Tags

Only include instances matching specific tags — useful for targeting a subset of infrastructure:

```yaml
plugin: crystian.incus.incus_inventory
tags:
  env: prod
  role: webserver
keyed_groups:
  - prefix: tag
    key: incus_user_tags
```

### Multi-Remote and Multi-Project

Query instances across multiple Incus remotes and projects:

```yaml
plugin: crystian.incus.incus_inventory
remotes:
  - local
  - staging-server
  - production-server
projects:
  - default
  - webapp
  - database
keyed_groups:
  - prefix: tag
    key: incus_user_tags
```

### Using in Playbooks

Target groups created by the plugin in your playbooks:

```yaml
# Deploy to all production web servers
- hosts: tag_env_prod:&tag_role_webserver
  tasks:
    - name: Deploy application
      ansible.builtin.copy:
        src: app/
        dest: /opt/app/

# Update all instances on a specific remote
- hosts: incus_remote_production
  tasks:
    - name: Update packages
      apt:
        upgrade: dist

# Configure all databases in the webapp project
- hosts: incus_project_webapp:&tag_role_database
  roles:
    - role: postgresql
      vars:
        pg_version: 15
```

### Ad-Hoc Commands

Run commands directly against inventory groups:

```bash
# Ping all production instances
ansible tag_env_prod -m ping

# Check disk usage on all web servers
ansible tag_role_webserver -a "df -h"

# Restart nginx on staging
ansible tag_env_staging:&tag_role_webserver -m service -a "name=nginx state=restarted"
```

### Advanced: Custom Groups and Variables with Compose

Use `groups` for conditional grouping and `compose` for dynamic host variables:

```yaml
plugin: crystian.incus.incus_inventory
keyed_groups:
  - prefix: tag
    key: incus_user_tags
  - prefix: os
    key: incus_config_image_os
groups:
  webservers: "'webserver' == tag_role"
  production: "'prod' == tag_env"
  high_memory: "incus_config_limits_memory | default('1GiB') | regex_search('[0-9]+') | int >= 4"
compose:
  ansible_user: "'ubuntu' if incus_config_image_os == 'ubuntu' else 'root'"
```

### Generate Static Inventory

Export the dynamic inventory to a static file for offline use or CI/CD:

```bash
# Full inventory as JSON
ansible-inventory -i incus_inventory.yml --list --output inventory.json

# Filtered inventory as YAML
ansible-inventory -i prod_incus_inventory.yml --list --yaml > prod_inventory.yml
```

For the complete reference, see [Inventory Plugin Documentation](docs/incus_inventory.md).

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

### Image Management
```yaml
- name: Copy image with properties
  crystian.incus.incus_image:
    alias: my-alpine
    source: images:alpine/edge
    properties:
      os: Alpine
      release: edge
      description: "Alpine Edge image"
    state: present

- name: Update properties (declarative - unlisted properties are removed)
  crystian.incus.incus_image:
    alias: my-alpine
    properties:
      os: Alpine
      release: latest
    state: present

- name: Set requirements properties
  crystian.incus.incus_image:
    alias: my-vm-image
    properties:
      os: Debian
      requirements.secureboot: "false"
      requirements.nesting: "true"
    state: present

- name: Import image from file
  crystian.incus.incus_image:
    alias: custom-image
    source: /tmp/image.tar.gz
    state: present

- name: Delete image
  crystian.incus.incus_image:
    alias: my-alpine
    state: absent
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
- Permissions to manage Incus (membership in `incus` group).
- Python virtual environment with `ansible-test` installed (`.venv/`).

### Setup

The `ansible-test` tool requires the collection to be in the standard directory structure. Copy the repository into the correct path before running tests:

```bash
# Copy collection to expected path
rm -rf ~/.ansible/collections/ansible_collections/crystian/incus
mkdir -p ~/.ansible/collections/ansible_collections/crystian/incus
cp -a . ~/.ansible/collections/ansible_collections/crystian/incus/

# Navigate to the collection directory
cd ~/.ansible/collections/ansible_collections/crystian/incus
```

### Running Integration Tests

You can run tests using `ansible-test` (standard for collections) or directly via `ansible-playbook` (faster for local development/debugging).

#### Method 1: ansible-test (Standard)
This is the official way to test Ansible collections. It sets up the environment and runs sanity checks.

```bash
# Run the full integration suite
.venv/bin/ansible-test integration -v --local

# Run a specific test target
.venv/bin/ansible-test integration incus_instance -v --local

# Resume from a specific target
.venv/bin/ansible-test integration --start-at incus_inventory -v --local
```

#### Method 2: ansible-playbook (Fast/Dev)
Useful for rapid iteration, debugging, and using specific optimization flags (`force_restore`, `skip-tags`).

**Cheat Sheet:**

| Goal | Command |
|---|---|
| **Run All Tests** | `ansible-playbook tests/integration.yml` |
| **Run Specific Tag** | `ansible-playbook tests/integration.yml --tags incus_instance` |
| **Reset Environment** | `ansible-playbook tests/integration.yml -e force_cleanup=true` |
| **Debug Specific Test** | `ansible-playbook tests/integration.yml --tags incus_inventory -vvv` |

> [!TIP]
> Combine flags for efficiency! For example, to run only inventory tests and force a snapshot restore:
> `ansible-playbook tests/integration.yml --tags incus_inventory -e force_restore=true`

### Snapshot Optimization
The test setup (infra/setup.yml) automatically creates a snapshot (`base-setup`) of the test VM after the first successful run. Subsequent runs will:
1. Detect the existing snapshot.
2. Restore the VM state instantly (skipping package installation).
3. Reuse the existing environment for tests.

To force a full rebuild (discarding snapshot):
```bash
ansible-playbook tests/integration.yml -e "force_cleanup=true"
```

To force a restore from snapshot (skipping successful setup check):
```bash
ansible-playbook tests/integration.yml -e "force_restore=true"
```

### Available Test Targets

| Target | Tests |
|--------|-------|
| `incus_admin_init` | Server initialization |
| `incus_instance` | Instance CRUD, rename, type |
| `incus_instance_cloud_init` | Cloud-init config and templates |
| `incus_config` | Instance config and devices |
| `incus_exec` | Command execution in instances |
| `incus_file` | File push/pull operations |
| `incus_export` | Instance backup export |
| `incus_image` | Image management and properties |
| `incus_info` | Resource information queries |
| `incus_list` | Instance listing with filters |
| `incus_inventory` | Dynamic inventory (tags, groups, compose) |
| `incus_lookup` | Lookup plugins (config, list, info, query) |
| `incus_network` | Network CRUD |
| `incus_network_forward` | Network forwards |
| `incus_profile` | Profile management |
| `incus_project` | Project management |
| `incus_remote` | Remote management |
| `incus_snapshot` | Snapshot management |
| `incus_storage` | Storage pools and volumes |

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
