# incus_instance (Module)

Manage Incus instances

Create, manage, and control Incus instances.
Supports create, delete, start, stop, restart, freeze, and unfreeze operations.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `name` | True |  |  | Name of the instance. |
| `remote` | False |  |  | Remote server to create the instance on. |
| `remote_image` | True |  |  | Image to use (e.g., 'images:debian/12'). |
| `started` | False | False |  | If true, ensure instance is started. If false, ensure instance is stopped. Ignored if state is 'absent'. |
| `state` | False | present | ['present', 'absent', 'restarted', 'frozen', 'unfrozen', 'rebuilt'] | State of the instance. present: Ensure instance exists (and started/stopped based on 'started' param). absent: Ensure instance is removed. restarted: Restart the instance. If stopped, starts it. frozen: Freeze (pause) a running instance. unfrozen: Unfreeze (resume) a frozen instance. rebuilt: Rebuild the instance root disk from a new image. |
| `force` | False | False |  | Force removal of running instances (only used when state='absent'). |
| `description` | False |  |  | Description of the instance. |
| `empty` | False | False |  | Create an empty instance. |
| `timeout` | False |  |  | Timeout in seconds for restart/stop operations. Uses Incus default if not specified. |
| `rebuild_image` | False |  |  | Image to use when rebuilding instance (state=rebuilt). Example: 'images:debian/12'. If not specified with state=rebuilt, rebuilds as empty. |
| `ephemeral` | False | False |  | Create an ephemeral instance. |
| `vm` | False | False |  | Create a virtual machine instead of a container. |
| `profiles` | False |  |  | List of profiles to apply to the instance. |
| `no_profiles` | False | False |  | Create the instance with no profiles. |
| `network` | False |  |  | Network name to attach to. |
| `storage` | False |  |  | Storage pool name. |
| `target` | False |  |  | Cluster member name to target. |
| `config` | False |  |  | Key/value pairs for instance configuration (e.g. {'limits.cpu': '2'}). |
| `devices` | False |  |  | Key/value pairs for device configuration. |
| `cloud_init_user_data` | False |  |  | Cloud-init user-data content. Sets 'cloud-init.user-data' config option. |
| `cloud_init_network_config` | False |  |  | Cloud-init network-config content. Sets 'cloud-init.network-config' config option. |
| `cloud_init_vendor_data` | False |  |  | Cloud-init vendor-data content. Sets 'cloud-init.vendor-data' config option. |
| `cloud_init_disk` | False | False |  | If true, attaches a 'cloud-init' disk device (source=cloud-init:config). Required for VMs without incus-agent or specific images. |
| `tags` | False |  |  | Dictionary of tags to apply to the instance. Maps to 'user.<key>' configuration keys. |
| `rename_from` | False |  |  | Name of an existing instance to rename to 'name'. |

## Examples

```yaml
- name: Create a container with cloud-init
  crystian.incus.incus_instance:
    name: my-web-server
    remote_image: images:ubuntu/22.04/cloud
    cloud_init_user_data: |
      #cloud-config
      package_upgrade: true
      packages:
        - nginx
- name: Restart an instance
  crystian.incus.incus_instance:
    name: my-web-server
    state: restarted

- name: Force restart an instance
  crystian.incus.incus_instance:
    name: my-web-server
    state: restarted
    force: true
    timeout: 30

- name: Freeze (pause) an instance
  crystian.incus.incus_instance:
    name: my-web-server
    state: frozen

- name: Unfreeze (resume) an instance
  crystian.incus.incus_instance:
    name: my-web-server
    state: unfrozen

- name: Rebuild instance with new image
  crystian.incus.incus_instance:
    name: my-web-server
    state: rebuilt
    rebuild_image: images:debian/13
    force: true

- name: Create a VM with cloud-init config disk
  crystian.incus.incus_instance:
    name: my-vm-server
    remote_image: images:debian/12/cloud
    vm: true
    cloud_init_disk: true
    cloud_init_user_data: "{{ lookup('file', 'user-data.yml') }}"
```

## Return Values

```yaml
instance:
  description: Instance information
  returned: always
  type: dict
```
