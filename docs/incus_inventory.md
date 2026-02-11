# incus_inventory (Inventory Plugin)

Incus inventory source

Get instances from Incus to be used as an inventory source.
Supports grouping by remote, project, and instance tags.
Automatically sets connection variables for the `community.general.incus` connection plugin.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `plugin` | True |  | ['crystian.incus.incus_inventory'] | Token that ensures this is a source file for the 'incus_inventory' plugin. |
| `remotes` | False | ['local'] |  | List of Incus remotes to search for instances. |
| `projects` | False | ['default'] | `INCUS_INVENTORY_PROJECTS` | List of Incus projects to search for instances. |
| `tags` | False | {} | `INCUS_INVENTORY_TAGS` | Filter instances by tags (user.<key>=<value>). |
| `running_only` | False | False |  | If true, only return running instances. |
| `keyed_groups` | False |  |  | Add hosts to group based on the values of a variable. |
| `groups` | False |  |  | Add hosts to group based on Jinja2 conditionals. |
| `compose` | False |  |  | Create vars from Jinja2 expressions. |

## Examples

```yaml
# Simple 'incus_inventory.yml'
plugin: crystian.incus.incus_inventory
remotes:
  - local
projects:
  - default
  - mywebproject

# Filter by tags
plugin: crystian.incus.incus_inventory
tags:
  env: prod
  owner: team-a

# Group by tags
plugin: crystian.incus.incus_inventory
keyed_groups:
  - prefix: tag
    key: incus_user_tags
```

## Dynamic Usage (Environment Variables)

You can override configuration using environment variables, useful for generating inventory files on the fly.

```bash
# Filter by environment tag
export INCUS_INVENTORY_TAGS='{"env": "prod"}'
ansible-inventory -i incus_inventory.yml --graph

# Filter by remote
export INCUS_INVENTORY_REMOTES='["myremote"]'
ansible-inventory -i incus_inventory.yml --graph
```

## Generating Static Inventory File

To generate a static `inventory.yml` file from the dynamic inventory:

```bash
# Generate inventory for all prod instances
export INCUS_INVENTORY_TAGS='{"env": "prod"}'
ansible-inventory -i incus_inventory.yml --list --yaml > inventory.yml

## Advanced Usage

### 1. Grouping by OS and Architecture via Keyed Groups
You can group hosts based on any Incus configuration key properly sanitized (dots and dashes replaced by underscores).

```yaml
plugin: crystian.incus.incus_inventory
keyed_groups:
  # Creates groups like 'os_debian', 'os_ubuntu'
  - prefix: os
    key: incus_config_image_os
  # Creates groups like 'arch_x86_64', 'arch_aarch64'
  - prefix: arch
    key: incus_config_image_architecture
```

### 2. Creating Custom Groups with Conditions
Use the `groups` option to create Ansible groups based on Jinja2 expressions.

```yaml
plugin: crystian.incus.incus_inventory
groups:
  # Group 'webservers' for hosts with tag service=web
  webservers: "'web' == tag_service"
  # Group 'production_db' for prod hosts that are databases
  production_db: "'prod' == tag_env and 'db' == tag_role"
  # Group for large instances
  high_performance: "incus_config_limits_cpu | default('1') | int >= 4"
```

### 3. Setting Variables with Compose
Use `compose` to dynamically set Ansible variables for hosts.

```yaml
plugin: crystian.incus.incus_inventory
compose:
  # Set ansible_user based on OS
  ansible_user: "'ubuntu' if incus_config_image_os == 'ubuntu' else 'root'"
  # Connect via internal IP if available (example logic)
  ansible_host: "incus_config_user_internal_ip | default(ansible_host)"
```

