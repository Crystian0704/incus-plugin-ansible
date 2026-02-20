#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incus_network
short_description: Manage Incus networks
description:
  - Manage Incus networks (create, delete, configure).
version_added: "1.0.0"
options:
  name:
    description:
      - Name of the network.
    required: true
    type: str
  state:
    description:
      - State of the network.
    required: false
    type: str
    choices: [ present, absent ]
    default: present
  type:
    description:
      - Type of the network (e.g., 'bridge', 'ovn', 'macvlan', 'sriov').
      - Only used during creation.
    required: false
    type: str
    default: bridge
  description:
    description:
      - Description of the network.
    required: false
    type: str
  config:
    description:
      - "Dictionary of configuration options (e.g., 'ipv4.address': '10.0.0.1/24')."
    required: false
    type: dict
  force:
    description:
      - Force deletion of the network even if instances are using it.
      - Only used with state=absent.
    required: false
    type: bool
    default: false
  project:
    description:
      - The project context.
      - Defaults to 'default'.
    required: false
    type: str
    default: default
  target:
    description:
      - Cluster member target.
    required: false
    type: str
  remote:
    description:
      - The remote server.
      - Defaults to 'local'.
    required: false
    type: str
    default: local
author:
  - Crystian @Crystian0704
'''

EXAMPLES = r'''
- name: Create a bridge network
  crystian.incus.incus_network:
    name: incusbr0
    type: bridge
    description: "My bridge network"
    config:
      ipv4.address: 10.0.0.1/24
      ipv4.nat: true
      ipv6.address: none

- name: Create an OVN network
  crystian.incus.incus_network:
    name: ovn-net
    type: ovn
    config:
      network: incusbr0

- name: Delete a network
  crystian.incus.incus_network:
    name: incusbr0
    state: absent
'''

RETURN = r'''
msg:
  description: Status message
  returned: always
  type: str
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess
import json
import os
import yaml

class IncusNetwork(object):
    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.state = module.params['state']
        self.type = module.params['type']
        self.description = module.params['description']
        self.config = module.params['config']
        self.force = module.params['force']
        self.project = module.params['project']
        self.target = module.params['target']
        self.remote = module.params['remote']

    def get_target_name(self):
        if self.remote and self.remote != 'local':
            return "{}:{}".format(self.remote, self.name)
        return self.name

    def run_incus(self, args, check_rc=True):
        cmd = ['incus']
        if self.project:
            cmd.extend(['--project', self.project])
        cmd.extend(args)
        
        env = os.environ.copy()
        env['LC_ALL'] = 'C'
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, env=env)
        stdout, stderr = p.communicate()
        
        if check_rc and p.returncode != 0:
             return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')
        
        return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

    def get_network(self):
        cmd = ['network', 'show', self.get_target_name()]
        if self.target:
            cmd.extend(['--target', self.target])
            
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc == 0:
            try:
                return yaml.safe_load(out)
            except:
                pass
        return None

    def create(self):
        cmd = ['network', 'create', self.get_target_name()]
        if self.type:
            cmd.extend(['--type', self.type])
        if self.target:
            cmd.extend(['--target', self.target])
            
        if self.config:
            for k, v in self.config.items():
                if v is not None:
                    cmd.append("{}={}".format(k, str(v).lower() if isinstance(v, bool) else v))

        if self.module.check_mode:
            self.module.exit_json(changed=True, msg="Network would be created")

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             self.module.fail_json(msg="Failed to create network: " + err, stdout=out, stderr=err)
        
        if self.description:
            self.update_description(force=True)
            
        self.module.exit_json(changed=True, msg="Network created")

    def update_description(self, force=False):
        if not self.description and not force:
            return False

        cmd = ['network', 'set', self.get_target_name(), 'description={}'.format(self.description), '--property']
        if self.target:
            cmd.extend(['--target', self.target])

        if self.module.check_mode:
             return True

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             self.module.fail_json(msg="Failed to update description: " + err, stdout=out, stderr=err)
        return True

    def update_configs(self, configs):
        cmd = ['network', 'set', self.get_target_name()]
        for k, v in configs.items():
            cmd.append("{}={}".format(k, v))
        if self.target:
            cmd.extend(['--target', self.target])

        if self.module.check_mode:
            return

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             self.module.fail_json(msg="Failed to update configs: " + err, stdout=out, stderr=err)

    def update_config(self, key, value):
        self.update_configs({key: value})

    def unset_config(self, key):
        cmd = ['network', 'unset', self.get_target_name(), key]
        if self.target:
            cmd.extend(['--target', self.target])

        if self.module.check_mode:
            return

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             self.module.fail_json(msg="Failed to unset config '{}': {}".format(key, err), stdout=out, stderr=err)

    def update(self):
        current = self.get_network()
        if not current:
            self.module.fail_json(msg="Network not found for update")

        changed = False
        
        current_desc = current.get('description', '')
        if self.description is not None and current_desc != self.description:
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Description would be updated")
            self.update_description()
            changed = True

        if self.config:
            current_config = current.get('config', {})
            to_set = {}
            to_unset = []

            for k, v in self.config.items():
                if v is None:
                    if k in current_config:
                        to_unset.append(k)
                    continue

                str_v = str(v).lower() if isinstance(v, bool) else str(v)
                if k not in current_config or str(current_config[k]) != str_v:
                    to_set[k] = str_v

            for k in to_unset:
                if self.module.check_mode:
                    self.module.exit_json(changed=True, msg="Config '{}' would be unset".format(k))
                self.unset_config(k)
                changed = True

            if to_set:
                if self.module.check_mode:
                    self.module.exit_json(changed=True, msg="Config items '{}' would be updated".format(list(to_set.keys())))
                self.update_configs(to_set)
                changed = True
        
        if not changed:
            self.module.exit_json(changed=False, msg="Network matches configuration")
        
        self.module.exit_json(changed=True, msg="Network updated")

    def delete(self):
        if self.module.check_mode:
             self.module.exit_json(changed=True, msg="Network would be deleted")

        cmd = ['network', 'delete', self.get_target_name()]
        if self.target:
            cmd.extend(['--target', self.target])

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             if not self.force and ('in use' in err.lower() or 'currently used' in err.lower()):
                 self.module.fail_json(
                     msg="Cannot delete network '{}': it is in use by instances. Use force=true to override.".format(self.name),
                     stdout=out, stderr=err)
             self.module.fail_json(msg="Failed to delete network: " + err, stdout=out, stderr=err)
        
        self.module.exit_json(changed=True, msg="Network deleted")

    def run(self):
        if self.state == 'present':
            if not self.get_network():
                self.create()
            else:
                self.update()
        elif self.state == 'absent':
            if self.get_network():
                self.delete()
            else:
                self.module.exit_json(changed=False, msg="Network already absent")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            type=dict(type='str', default='bridge', required=False),
            description=dict(type='str', required=False),
            config=dict(type='dict', required=False),
            force=dict(type='bool', default=False),
            project=dict(type='str', default='default', required=False),
            target=dict(type='str', required=False),
            remote=dict(type='str', default='local', required=False),
        ),
        supports_check_mode=True,
    )

    manager = IncusNetwork(module)
    manager.run()

if __name__ == '__main__':
    main()
