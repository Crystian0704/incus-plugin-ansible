# incus_admin_init (Module)

Initialize Incus server

Initialize an Incus server using a YAML preseed configuration.
Wraps 'incus admin init --preseed'.
Idempotency is handled by checking if the server seems initialized (e.g. has storage pools).

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `config` | True |  |  | The preseed configuration as a dictionary. Structure should match the YAML format expected by 'incus admin init --preseed'. |
| `remote` | False |  |  | The remote Incus server to initialize. Defaults to 'local'. |
| `force` | False | False |  | Force initialization even if the server appears to be already initialized. {'WARNING': 'This may fail if resources already exist or cause data loss depending on the config.'} |

## Examples

```yaml
- name: Initialize Incus
  crystian.incus.incus_admin_init:
    config:
      config: {}
      networks:
        - config:
            ipv4.address: auto
            ipv6.address: auto
          description: ""
          name: incusbr0
          type: ""
          project: default
      storage_pools:
        - config:
            source: /var/lib/incus/storage-pools/default
          description: ""
          name: default
          driver: dir
      profiles:
        - config: {}
          description: ""
          devices:
            eth0:
              name: eth0
              network: incusbr0
              type: nic
            root:
              path: /
              pool: default
              type: disk
          name: default
      projects: []
      cluster: null
```

## Return Values

```yaml
# Standard Ansible return values
```
