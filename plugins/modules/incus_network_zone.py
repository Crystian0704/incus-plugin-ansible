#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incus_network_zone
short_description: Manage Incus network zones
description:
  - Manage Incus network zones (create, delete, configure).
version_added: "1.0.0"
options:
  name:
    description:
      - Name of the network zone.
    required: true
    type: str
  state:
    description:
      - State of the network zone.
    required: false
    type: str
    choices: [ present, absent ]
    default: present
  description:
    description:
      - Description of the network zone.
    required: false
    type: str
  config:
    description:
      - Dictionary of configuration options.
    required: false
    type: dict
  project:
    description:
      - The project context.
      - Defaults to 'default'.
    required: false
    type: str
    default: default
  remote:
    description:
      - Remote Incus server.
      - Defaults to 'local'.
    required: false
    type: str
    default: local
author:
  - Crystian @Crystian0704
'''

EXAMPLES = r'''
- name: Create a network zone
  crystian.incus.incus_network_zone:
    name: incus.test
    description: "Internal DNS zone"
    config:
      dns.domain: incus.test

- name: Delete a network zone
  crystian.incus.incus_network_zone:
    name: incus.test
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

class IncusNetworkZone(object):
    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.state = module.params['state']
        self.description = module.params['description']
        self.config = module.params['config']
        self.project = module.params['project']
        self.remote = module.params['remote']

    def get_target_name(self):
        if self.remote and self.remote != 'local':
            return "{}:{}".format(self.remote, self.name)
        return self.name

    def run_incus(self, args, check_rc=True, stdin=None):
        cmd = ['incus']
        if self.project:
            cmd.extend(['--project', self.project])
        cmd.extend(args)
        
        env = os.environ.copy()
        env['LC_ALL'] = 'C'
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, env=env)
        stdout, stderr = p.communicate(input=stdin.encode('utf-8') if stdin else None)
        
        if check_rc and p.returncode != 0:
             return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')
        
        return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

    def get_zone(self):
        cmd = ['network', 'zone', 'show', self.get_target_name()]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc == 0:
            try:
                return yaml.safe_load(out)
            except:
                pass
        return None

    def create_or_update(self):
        current = self.get_zone()
        
        desired = {
            'name': self.name,
            'description': self.description if self.description is not None else (current.get('description', '') if current else ''),
            'config': self.config if self.config is not None else (current.get('config', {}) if current else {})
        }

        if current:
            changes_needed = False
            
            if self.description is not None and current.get('description') != self.description:
                changes_needed = True
            
            if self.config is not None and current.get('config') != self.config:
                changes_needed = True

            if not changes_needed:
                self.module.exit_json(changed=False, msg="Network zone matches configuration")

            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Network zone would be updated")

            rc, out, err = self.run_incus(['network', 'zone', 'edit', self.get_target_name()], stdin=yaml.dump(desired))
            if rc != 0:
                self.module.fail_json(msg="Failed to update network zone: " + err, stdout=out, stderr=err)
            
            self.module.exit_json(changed=True, msg="Network zone updated")

        else:
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Network zone would be created")
            
            cmd = ['network', 'zone', 'create', self.get_target_name()]
            rc, out, err = self.run_incus(cmd)
            if rc != 0:
                self.module.fail_json(msg="Failed to create network zone: " + err, stdout=out, stderr=err)
            
            rc, out, err = self.run_incus(['network', 'zone', 'edit', self.get_target_name()], stdin=yaml.dump(desired))
            if rc != 0:
                 self.run_incus(['network', 'zone', 'delete', self.get_target_name()], check_rc=False)
                 self.module.fail_json(msg="Failed to configure created network zone: " + err, stdout=out, stderr=err)

            self.module.exit_json(changed=True, msg="Network zone created")

    def delete(self):
        if self.module.check_mode:
             self.get_zone() 
             if self.get_zone():
                self.module.exit_json(changed=True, msg="Network zone would be deleted")
             else:
                self.module.exit_json(changed=False, msg="Network zone already absent")

        if not self.get_zone():
            self.module.exit_json(changed=False, msg="Network zone already absent")

        cmd = ['network', 'zone', 'delete', self.get_target_name()]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             self.module.fail_json(msg="Failed to delete network zone: " + err, stdout=out, stderr=err)
        
        self.module.exit_json(changed=True, msg="Network zone deleted")

    def run(self):
        if self.state == 'present':
            self.create_or_update()
        elif self.state == 'absent':
            self.delete()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            description=dict(type='str', required=False),
            config=dict(type='dict', required=False),
            project=dict(type='str', default='default', required=False),
            remote=dict(type='str', default='local', required=False),
        ),
        supports_check_mode=True,
    )

    manager = IncusNetworkZone(module)
    manager.run()

if __name__ == '__main__':
    main()
