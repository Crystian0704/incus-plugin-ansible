#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incus_network_acl
short_description: Manage Incus network ACLs
description:
  - Manage Incus network ACLs (create, delete, configure).
version_added: "1.0.0"
options:
  name:
    description:
      - Name of the ACL.
    required: true
    type: str
  state:
    description:
      - State of the ACL.
    required: false
    type: str
    choices: [ present, absent ]
    default: present
  description:
    description:
      - Description of the ACL.
    required: false
    type: str
  egress:
    description:
      - List of egress rules.
    required: false
    type: list
    elements: dict
  ingress:
    description:
      - List of ingress rules.
    required: false
    type: list
    elements: dict
  config:
    description:
      - Dictionary of configuration options.
    required: false
    type: dict
  force:
    description:
      - Force deletion of the ACL even if it is referenced by networks.
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
- name: Create a network ACL
  crystian.incus.incus_network_acl:
    name: my-acl
    description: "My custom ACL"
    ingress:
      - action: allow
        protocol: tcp
        destination_port: 80
    egress:
      - action: allow
        protocol: tcp
        destination_port: 80
    config:
      user.mykey: myvalue

- name: Delete a network ACL
  crystian.incus.incus_network_acl:
    name: my-acl
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

class IncusNetworkACL(object):
    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.state = module.params['state']
        self.description = module.params['description']
        self.egress = module.params['egress']
        self.ingress = module.params['ingress']
        self.config = module.params['config']
        self.force = module.params['force']
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

    def get_acl(self):
        cmd = ['network', 'acl', 'show', self.get_target_name()]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc == 0:
            try:
                return yaml.safe_load(out)
            except:
                pass
        return None

    def create_or_update(self):
        current = self.get_acl()
        
        desired = {
            'name': self.name,
            'description': self.description if self.description is not None else (current.get('description', '') if current else ''),
            'egress': self.egress if self.egress is not None else (current.get('egress', []) if current else []),
            'ingress': self.ingress if self.ingress is not None else (current.get('ingress', []) if current else []),
            'config': self.config if self.config is not None else (current.get('config', {}) if current else {})
        }

        if current:
            changes_needed = False
            
            if self.description is not None and current.get('description') != self.description:
                changes_needed = True
            
            if self.egress is not None and current.get('egress') != self.egress:
                changes_needed = True

            if self.ingress is not None and current.get('ingress') != self.ingress:
                changes_needed = True

            if self.config is not None:
                if current.get('config') != self.config:
                    changes_needed = True

            if not changes_needed:
                self.module.exit_json(changed=False, msg="ACL matches configuration")

            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="ACL would be updated")

            rc, out, err = self.run_incus(['network', 'acl', 'edit', self.get_target_name()], stdin=yaml.dump(desired))
            if rc != 0:
                self.module.fail_json(msg="Failed to update ACL: " + err, stdout=out, stderr=err)
            
            self.module.exit_json(changed=True, msg="ACL updated")

        else:
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="ACL would be created")
            
            cmd = ['network', 'acl', 'create', self.get_target_name()]
            rc, out, err = self.run_incus(cmd)
            if rc != 0:
                self.module.fail_json(msg="Failed to create ACL: " + err, stdout=out, stderr=err)
            
            rc, out, err = self.run_incus(['network', 'acl', 'edit', self.get_target_name()], stdin=yaml.dump(desired))
            if rc != 0:
                 self.run_incus(['network', 'acl', 'delete', self.get_target_name()], check_rc=False)
                 self.module.fail_json(msg="Failed to configure created ACL: " + err, stdout=out, stderr=err)

            self.module.exit_json(changed=True, msg="ACL created")

    def delete(self):
        if self.module.check_mode:
             self.get_acl() 
             if self.get_acl():
                self.module.exit_json(changed=True, msg="ACL would be deleted")
             else:
                self.module.exit_json(changed=False, msg="ACL already absent")

        if not self.get_acl():
            self.module.exit_json(changed=False, msg="ACL already absent")

        cmd = ['network', 'acl', 'delete', self.get_target_name()]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             if not self.force and ('in use' in err.lower() or 'currently used' in err.lower() or 'referenced' in err.lower()):
                 self.module.fail_json(
                     msg="Cannot delete ACL '{}': it is referenced by networks. Use force=true to override.".format(self.name),
                     stdout=out, stderr=err)
             self.module.fail_json(msg="Failed to delete ACL: " + err, stdout=out, stderr=err)
        
        self.module.exit_json(changed=True, msg="ACL deleted")

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
            egress=dict(type='list', elements='dict', required=False),
            ingress=dict(type='list', elements='dict', required=False),
            config=dict(type='dict', required=False),
            force=dict(type='bool', default=False),
            project=dict(type='str', default='default', required=False),
            remote=dict(type='str', default='local', required=False),
        ),
        supports_check_mode=True,
    )

    manager = IncusNetworkACL(module)
    manager.run()

if __name__ == '__main__':
    main()
