#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r'''
---
module: incus_instance
short_description: Manage Incus instances
description:
  - Create, manage, and control Incus instances.
  - 'Supports create, delete, start, stop, restart, freeze, and unfreeze operations.'
version_added: "1.0.0"
options:
  name:
    description:
      - Name of the instance.
    required: true
    type: str
  remote:
    description:
      - Remote server to create the instance on.
    required: false
    type: str
  remote_image:
    description:
      - Image to use (e.g., 'images:debian/12').
    required: true
    type: str
  started:
    description:
      - If true, ensure instance is started.
      - If false, ensure instance is stopped.
      - Ignored if state is 'absent'.
    type: bool
    default: false
    required: false
  state:
    description:
      - State of the instance.
      - "present: Ensure instance exists (and started/stopped based on 'started' param)."
      - "absent: Ensure instance is removed."
      - "restarted: Restart the instance. If stopped, starts it."
      - "frozen: Freeze (pause) a running instance."
      - "unfrozen: Unfreeze (resume) a frozen instance."
      - "rebuilt: Rebuild the instance root disk from a new image."
    type: str
    choices: ['present', 'absent', 'restarted', 'frozen', 'unfrozen', 'rebuilt']
    default: present
    required: false
  force:
    description:
      - Force removal of running instances (only used when state='absent').
    type: bool
    default: false
    required: false
  description:
    description:
      - Description of the instance.
    type: str
    required: false
  empty:
    description:
      - Create an empty instance.
    type: bool
    required: false
    default: false
  timeout:
    description:
      - Timeout in seconds for restart/stop operations.
      - Uses Incus default if not specified.
    type: int
    required: false
  rebuild_image:
    description:
      - Image to use when rebuilding instance (state=rebuilt).
      - "Example: 'images:debian/12'."
      - If not specified with state=rebuilt, rebuilds as empty.
    type: str
    required: false
  ephemeral:
    description:
      - Create an ephemeral instance.
    type: bool
    required: false
    default: false
  vm:
    description:
      - Create a virtual machine instead of a container.
    type: bool
    required: false
    default: false

  profiles:
    description:
      - List of profiles to apply to the instance.
    type: list
    elements: str
    required: false
  no_profiles:
    description:
      - Create the instance with no profiles.
    type: bool
    required: false
    default: false
  network:
    description:
      - Network name to attach to.
    type: str
    required: false
  storage:
    description:
      - Storage pool name.
    type: str
    required: false
  target:
    description:
      - Cluster member name to target.
    type: str
    required: false
  config:
    description:
      - "Key/value pairs for instance configuration (e.g. {'limits.cpu': '2'})."
    type: dict
    required: false
  devices:
    description:
      - Key/value pairs for device configuration.
    type: dict
    required: false
  cloud_init_user_data:
    description:
      - Cloud-init user-data content.
      - Sets 'cloud-init.user-data' config option.
    type: str
    required: false
  cloud_init_network_config:
    description:
      - Cloud-init network-config content.
      - Sets 'cloud-init.network-config' config option.
    type: str
    required: false
  cloud_init_vendor_data:
    description:
      - Cloud-init vendor-data content.
      - Sets 'cloud-init.vendor-data' config option.
    type: str
    required: false
  cloud_init_disk:
    description:
      - If true, attaches a 'cloud-init' disk device (source=cloud-init:config).
      - Required for VMs without incus-agent or specific images.
    type: bool
    default: false
    required: false
  tags:
    description:
      - Dictionary of tags to apply to the instance.
      - Maps to 'user.<key>' configuration keys.
    type: dict
    required: false
  project:
    description:
      - The project instance belongs to.
    required: false
    type: str
    default: default
  rename_from:
    description:
      - Name of an existing instance to rename to 'name'.
    type: str
    required: false
author:
  - Crystian @Crystian0704
'''
EXAMPLES = r'''
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
'''
RETURN = r'''
instance:
  description: Instance information
  returned: always
  type: dict
'''
from ansible.module_utils.basic import AnsibleModule
import subprocess
import json
import shlex
class IncusInstance(object):
    def __init__(self, module):
        self.module = module
        self.name_param = module.params['name']
        self.rename_from = module.params.get('rename_from')
        self.remote = module.params['remote']
        self.remote_image = module.params['remote_image']
        self.state = module.params['state']
        self.empty = module.params.get('empty', False)
        self.name = self.name_param
        if self.remote:
            self.name = "{}:{}".format(self.remote, self.name_param)
        self.started = module.params['started']
        self.state = module.params['state']
        self.force = module.params['force']
        self.vm = module.params['vm']
        self.ephemeral = module.params['ephemeral']
        self.profiles = module.params['profiles']
        self.no_profiles = module.params['no_profiles']
        self.config = module.params['config'] or {}
        self.devices = module.params['devices'] or {}
        self.storage = module.params['storage']
        self.network = module.params['network']
        self.target = module.params['target']
        self.description = module.params['description']
        self.empty = module.params.get('empty', False)
        self.timeout = module.params.get('timeout')
        self.rebuild_image = module.params.get('rebuild_image')
        self.project = module.params.get('project')
        self.user_data = module.params.get('cloud_init_user_data')
        self.network_config = module.params.get('cloud_init_network_config')
        self.vendor_data = module.params.get('cloud_init_vendor_data')
        self.cloud_init_disk = module.params.get('cloud_init_disk')
        self.tags = module.params.get('tags')
        
        if self.tags:
            for k, v in self.tags.items():
                self.config['user.{}'.format(k)] = v
                
        if self.user_data:
            self.config['cloud-init.user-data'] = self.user_data
        if self.network_config:
            self.config['cloud-init.network-config'] = self.network_config
        if self.vendor_data:
            self.config['cloud-init.vendor-data'] = self.vendor_data
        if self.cloud_init_disk:
            if 'cloud-init' not in self.devices:
                self.devices['cloud-init'] = {'type': 'disk', 'source': 'cloud-init:config'}
        self.incus_path = module.get_bin_path('incus', required=True)
    def _run_command(self, cmd, check_rc=True):
        if self.project and self.project != 'default':
            if '--project' not in cmd:
                 cmd.insert(1, self.project)
                 cmd.insert(1, '--project')
        try:
            rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
            if check_rc and rc != 0:
                self.module.fail_json(msg="Command execution failed", cmd=cmd, rc=rc, stdout=out, stderr=err)
            return rc, out, err
        except Exception as e:
            self.module.fail_json(msg="Command execution exception: %s" % str(e), cmd=cmd)
    def get_instance_info(self, name=None):
        instance_name = name if name else self.name
        prefix = ""
        if ":" in instance_name:
             parts = instance_name.split(':', 1)
             prefix = parts[0] + ":"
             instance_name = parts[1]
        elif not name and self.remote:
             prefix = self.remote + ":"

        if name and ":" in name:
             pass
        elif name and self.remote:
             prefix = self.remote + ":"
        
        cmd = [self.incus_path, 'list', '--format=json', '{}^{}$'.format(prefix, instance_name)]
        rc, out, err = self._run_command(cmd, check_rc=False)
        if rc == 0:
            try:
                data = json.loads(out)
                if data and len(data) > 0:
                    return data[0]
            except ValueError:
                pass
            return None
        return None
    def create_instance(self):
        if not self.remote_image and not self.empty:
             self.module.fail_json(msg="remote_image is required when creating an instance (state=present)")
                     
        image_src = self.remote_image
        if self.remote and self.remote != 'local':
             if ':' not in image_src:
                  image_src = "{}:{}".format(self.remote, image_src)
                  
        cmd = [self.incus_path, 'init', image_src, self.name]
        if self.vm:
            cmd.append('--vm')
        if self.ephemeral:
            cmd.append('--ephemeral')
        if self.empty:
            cmd.append('--empty')
        if self.no_profiles:
            cmd.append('--no-profiles')
        elif self.profiles:
            for p in self.profiles:
                cmd.extend(['--profile', p])
        if self.network:
             cmd.extend(['--network', self.network])
        if self.storage:
             cmd.extend(['--storage', self.storage])
        if self.target:
             cmd.extend(['--target', self.target])
        if self.config:
            for k, v in self.config.items():
                cmd.extend(['--config', '{}={}'.format(k, v)]) 
        if self.description:
             cmd.extend(['--description', self.description])
        self._run_command(cmd)

    def start_instance(self):
        cmd = [self.incus_path, 'start', self.name]
        self._run_command(cmd)

    def stop_instance(self):
        cmd = [self.incus_path, 'stop', self.name]
        if self.force:
            cmd.append('--force')
        if self.timeout is not None:
            cmd.extend(['--timeout', str(self.timeout)])
        self._run_command(cmd)

    def restart_instance(self):
        cmd = [self.incus_path, 'restart', self.name]
        if self.force:
            cmd.append('--force')
        if self.timeout is not None:
            cmd.extend(['--timeout', str(self.timeout)])
        self._run_command(cmd)

    def pause_instance(self):
        cmd = [self.incus_path, 'pause', self.name]
        self._run_command(cmd)

    def resume_instance(self):
        cmd = [self.incus_path, 'resume', self.name]
        self._run_command(cmd)

    def rebuild_instance(self):
        if self.rebuild_image:
            cmd = [self.incus_path, 'rebuild', self.rebuild_image, self.name]
        else:
            cmd = [self.incus_path, 'rebuild', self.name, '--empty']
        if self.force:
            cmd.append('--force')
        self._run_command(cmd)

    def delete_instance(self):
        cmd = [self.incus_path, 'delete', self.name]
        if self.force:
            cmd.append('--force')
        self._run_command(cmd)

    def get_instance_state(self):
        instance_name = self.name_param
        remote_prefix = ""
        if ":" in self.name_param:
            parts = self.name_param.split(':', 1)
            remote_prefix = parts[0] + ":"
            instance_name = parts[1]
        elif self.remote:
             remote_prefix = self.remote + ":"
        query_path = "{}/1.0/instances/{}/state".format(remote_prefix, instance_name)
        cmd = [self.incus_path, 'query', query_path]
        rc, out, err = self._run_command(cmd, check_rc=False)
        if rc == 0:
            try:
                return json.loads(out)
            except ValueError:
                pass
        return None

    def configure_devices(self):
        if not self.devices:
            return
        info = self.get_instance_info()
        current_devices = info.get('devices', {}) if info else {}
        for device_name, device_config in self.devices.items():
             if device_name in current_devices:
                 continue 
             cfg = device_config.copy()
             dtype = cfg.pop('type', None)
             if not dtype:
                 self.module.fail_json(msg="Device '{}' missing required 'type'".format(device_name))
             cmd = [self.incus_path, 'config', 'device', 'add', self.name, device_name, dtype]
             for k, v in cfg.items():
                 cmd.append('{}={}'.format(k, v))
             self._run_command(cmd)

    def configure_config(self):
        if not self.config:
            return False
            
        info = self.get_instance_info()
        current_config = info.get('config', {}) if info else {}
        changed = False
        
        for k, v in self.config.items():
            if current_config.get(k) != str(v):
                cmd = [self.incus_path, 'config', 'set', self.name, k, str(v)]
                self._run_command(cmd)
                changed = True
        return changed

    def configure_profiles(self):
        if self.profiles is None:
            return False
            
        info = self.get_instance_info()
        current_profiles = info.get('profiles', []) if info else []
        
        if sorted(current_profiles) != sorted(self.profiles):
            if self.module.check_mode:
                return True
            
            profiles_arg = ','.join(self.profiles)
            cmd = [self.incus_path, 'profile', 'assign', self.name, profiles_arg]
            self._run_command(cmd)
            return True
        return False

    def rename_instance(self):
        source = self.rename_from
        target = self.name_param

        if self.remote:
            source = "{}:{}".format(self.remote, source)
            target = "{}:{}".format(self.remote, target)
        
        cmd = [self.incus_path, 'move', source, target]
        self._run_command(cmd)

    def run(self):
        changed = False
        if self.state == 'present' and self.rename_from:
             source_info = self.get_instance_info(self.rename_from)
             target_info = self.get_instance_info()
             
             if source_info and not target_info:
                 if self.module.check_mode:
                     self.module.exit_json(changed=True, msg="Instance would be renamed")
                 self.rename_instance()
                 changed = True
             elif not source_info and not target_info:
                 self.module.fail_json(msg="Source instance '{}' for rename not found".format(self.rename_from))
             
        info = self.get_instance_info()

        if self.state == 'absent':
            if info:
                if self.module.check_mode:
                    self.module.exit_json(changed=True, msg="Instance would be deleted")
                self.delete_instance()
                changed = True
                self.module.exit_json(changed=changed, instance=None, state=None)
            else:
                self.module.exit_json(changed=False, msg="Instance already absent")

        elif self.state == 'present':
            if not info:
                if self.module.check_mode:
                    self.module.exit_json(changed=True, msg="Instance would be created")
                self.create_instance()
                self.configure_devices()
                changed = True
                info = self.get_instance_info()
                if not info:
                     self.module.fail_json(msg="Instance created but could not be retrieved.", name=self.name)
            else:
                if self.configure_config():
                    changed = True
                self.configure_devices()
                if self.configure_profiles():
                    changed = True 

            current_status = info['status'].lower()
            
            if self.started and current_status == 'stopped':
                 if self.module.check_mode:
                     self.module.exit_json(changed=True, msg="Instance would be started")
                 self.start_instance()
                 changed = True
            elif not self.started and current_status == 'running':
                 if self.module.check_mode:
                     self.module.exit_json(changed=True, msg="Instance would be stopped")
                 self.stop_instance()
                 changed = True

            if changed:
                info = self.get_instance_info()
            
            state_info = self.get_instance_state()
            self.module.exit_json(changed=changed, instance=info, state=state_info)

        elif self.state == 'restarted':
            if not info:
                self.module.fail_json(msg="Instance '{}' not found, cannot restart".format(self.name_param))
            current_status = info['status'].lower()
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Instance would be restarted")
            if current_status == 'stopped':
                self.start_instance()
            else:
                self.restart_instance()
            info = self.get_instance_info()
            state_info = self.get_instance_state()
            self.module.exit_json(changed=True, instance=info, state=state_info)

        elif self.state == 'frozen':
            if not info:
                self.module.fail_json(msg="Instance '{}' not found, cannot freeze".format(self.name_param))
            current_status = info['status'].lower()
            if current_status == 'frozen':
                self.module.exit_json(changed=False, msg="Instance already frozen", instance=info)
            if current_status != 'running':
                self.module.fail_json(msg="Instance '{}' must be running to freeze (current status: {})".format(self.name_param, current_status))
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Instance would be frozen")
            self.pause_instance()
            info = self.get_instance_info()
            state_info = self.get_instance_state()
            self.module.exit_json(changed=True, instance=info, state=state_info)

        elif self.state == 'unfrozen':
            if not info:
                self.module.fail_json(msg="Instance '{}' not found, cannot unfreeze".format(self.name_param))
            current_status = info['status'].lower()
            if current_status == 'running':
                self.module.exit_json(changed=False, msg="Instance already running", instance=info)
            if current_status != 'frozen':
                self.module.fail_json(msg="Instance '{}' must be frozen to unfreeze (current status: {})".format(self.name_param, current_status))
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Instance would be unfrozen")
            self.resume_instance()
            info = self.get_instance_info()
            state_info = self.get_instance_state()
            self.module.exit_json(changed=True, instance=info, state=state_info)

        elif self.state == 'rebuilt':
            if not info:
                self.module.fail_json(msg="Instance '{}' not found, cannot rebuild".format(self.name_param))
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Instance would be rebuilt")
            self.rebuild_instance()
            info = self.get_instance_info()
            state_info = self.get_instance_state()
            self.module.exit_json(changed=True, instance=info, state=state_info)
def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            remote=dict(type='str', default='local', required=False),
            remote_image=dict(type='str', required=False),
            started=dict(type='bool', default=False, required=False),
            state=dict(type='str', choices=['present', 'absent', 'restarted', 'frozen', 'unfrozen', 'rebuilt'], default='present', required=False),
            force=dict(type='bool', default=False, required=False),
            description=dict(type='str', required=False),
            empty=dict(type='bool', default=False),
            ephemeral=dict(type='bool', default=False),
            vm=dict(type='bool', default=False),
            profiles=dict(type='list', elements='str', required=False),
            no_profiles=dict(type='bool', default=False),
            network=dict(type='str', required=False),
            storage=dict(type='str', required=False),
            target=dict(type='str', required=False),
            config=dict(type='dict', required=False),
            devices=dict(type='dict', required=False),
            project=dict(type='str', default='default', required=False),
            cloud_init_user_data=dict(type='str', required=False),
            cloud_init_network_config=dict(type='str', required=False),
            cloud_init_vendor_data=dict(type='str', required=False),
            cloud_init_disk=dict(type='bool', default=False, required=False),
            rename_from=dict(type='str', required=False),
            tags=dict(type='dict', required=False),
            timeout=dict(type='int', required=False),
            rebuild_image=dict(type='str', required=False),
        ),
        supports_check_mode=True,
    )
    creator = IncusInstance(module)
    creator.run()
if __name__ == '__main__':
    main()
