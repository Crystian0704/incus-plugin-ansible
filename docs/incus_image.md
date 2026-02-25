# incus_image (Module)

Manage Incus images

Manage images in the Incus image store.
Supports copying from remotes, importing from files, exporting to files, and deleting.

## Parameters

| Parameter | Required | Default | Choices | Description |
|---|---|---|---|---|
| `alias` | False |  |  | Alias of the image. Used as the primary identifier for presence checks if fingerprint is not provided. |
| `fingerprint` | False |  |  | Fingerprint of the image. If provided, used to verify the exact image identity. |
| `state` | False | present | ['present', 'absent', 'exported', 'info'] | State of the image. {'present': 'Ensure image exists (copy or import if missing).'} {'absent': 'Ensure image is removed.'} {'exported': 'Export image to file.'} {'info': 'Retrieve information about images.'} |
| `source` | False |  |  | Source for the image when state='present'. Can be a remote image (e.g. 'images:alpine/edge') or a local file path. If it looks like a file path, it is treated as an import. If it looks like a remote:alias, it is treated as a copy. |
| `dest` | False |  |  | Destination path for exported image (when state='exported'). |
| `properties` | False |  |  | Dictionary of properties to set on the image. Uses declarative behavior - properties not listed will be removed from the image. Supports special properties like C(requirements.secureboot), C(requirements.nesting), etc. |
| `aliases` | False |  |  | List of additional aliases to assign to the image. |
| `public` | False | False |  | Whether the image should be public. |
| `copy_aliases` | False | False |  | Copy aliases from source. |
| `mode` | False | pull | ['pull', 'push', 'relay'] | Transfer mode. One of pull, push or relay. |
| `profiles` | False |  |  | List of profiles to apply to the new image. |
| `target_project` | False |  |  | Copy to a different project from the source. |
| `vm` | False | False |  | Copy virtual machine images. |
| `auto_update` | False | False |  | Whether to auto-update the image (valid for remote copies). |
| `refresh` | False | False |  | Whether to refresh the image from the remote source if it already exists. |
| `remote` | False | local |  | The remote server. Defaults to 'local'. |
| `project` | False | default |  | The project instance belongs to. Defaults to 'default'. |

## Examples

```yaml
- name: Copy alpine image from images remote
  crystian.incus.incus_image:
    alias: my-alpine
    source: images:alpine/edge
    state: present

- name: Copy image with properties
  crystian.incus.incus_image:
    alias: my-alpine
    source: images:alpine/edge
    properties:
      os: Alpine
      release: edge
      description: "Alpine Edge image"
    state: present

- name: Copy image with auto-update and aliases
  crystian.incus.incus_image:
    alias: my-alpine
    source: images:alpine/edge
    auto_update: true
    aliases:
      - alpine-edge
      - alpine-latest
    state: present

- name: Import image from local file with properties
  crystian.incus.incus_image:
    alias: custom-image
    source: /tmp/image.tar.gz
    properties:
      os: Debian
      requirements.secureboot: "false"
    state: present

- name: Update properties on existing image (declarative - unlisted are removed)
  crystian.incus.incus_image:
    alias: my-alpine
    properties:
      os: Alpine
      release: latest
    state: present

- name: Set requirements properties on VM image
  crystian.incus.incus_image:
    alias: my-vm-image
    properties:
      requirements.secureboot: "false"
      requirements.nesting: "true"
    state: present

- name: Copy image to remote server
  crystian.incus.incus_image:
    alias: my-alpine
    source: images:alpine/edge
    remote: production
    public: true
    state: present

- name: Export image to file
  crystian.incus.incus_image:
    alias: my-alpine
    dest: /tmp/my-alpine-backup.tar.gz
    state: exported

- name: Delete image
  crystian.incus.incus_image:
    alias: my-alpine
    state: absent

- name: Retrieve image info by alias
  crystian.incus.incus_image:
    alias: my-alpine
    state: info

- name: List all remote images
  crystian.incus.incus_image:
    remote: my-remote
    state: info
```

## Return Values

```yaml
msg:
  description: Status message
  returned: always
  type: str
fingerprint:
  description: Fingerprint of the managed image
  returned: when available
  type: str
properties:
  description: Current properties of the image after changes
  returned: when available
  type: dict
images:
  description: List of images matching the request (for state=info)
  returned: when state=info
  type: list
  elements: dict
```
