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
| `projects` | False | ['default'] |  | List of Incus projects to search for instances. |
| `tags` | False | {} |  | Filter instances by tags (user.<key>=<value>). |
| `running_only` | False | False |  | If true, only return running instances. |

## Examples

```yaml
# Basic usage
plugin: crystian.incus.incus_inventory
remotes:
  - local
projects:
  - default
  - mywebproject

# Group by tags
plugin: crystian.incus.incus_inventory
keyed_groups:
  - prefix: tag
    key: incus_user_tags

# Filter by tags
plugin: crystian.incus.incus_inventory
tags:
  env: prod

# Group by OS and architecture
plugin: crystian.incus.incus_inventory
keyed_groups:
  - prefix: os
    key: incus_config_image_os
  - prefix: arch
    key: incus_config_image_architecture

# Custom groups with conditions
plugin: crystian.incus.incus_inventory
groups:
  webservers: "'web' == tag_service"
  production_db: "'prod' == tag_env and 'db' == tag_role"
  high_performance: "incus_config_limits_cpu | default('1') | int >= 4"

# Setting variables with compose
plugin: crystian.incus.incus_inventory
compose:
  ansible_user: "'ubuntu' if incus_config_image_os == 'ubuntu' else 'root'"
  ansible_host: "incus_config_user_internal_ip | default(ansible_host)"
```

## Return Values

