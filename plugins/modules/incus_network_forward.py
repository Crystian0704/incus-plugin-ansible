#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incus_network_forward
short_description: Manage Incus network forwards
description:
  - Manage Incus network forwards (create, delete, configure, port mapping).
version_added: "1.0.0"
options:
  network:
    description:
      - Name of the network.
    required: true
    type: str
  listen_address:
    description:
      - The listen IP address for the forward.
    required: true
    type: str
  state:
    description:
      - State of the network forward.
    required: false
    type: str
    choices: [ present, absent ]
    default: present
  description:
    description:
      - Description of the network forward.
    required: false
    type: str
  config:
    description:
      - Dictionary of configuration options (e.g. target_address).
    required: false
    type: dict
  ports:
    description:
      - List of port specifications.
    required: false
    type: list
    elements: dict
    suboptions:
      protocol:
        description: Protocol (tcp or udp).
        type: str
        choices: [ tcp, udp ]
        required: true
      listen_port:
        description: Port(s) to listen on (e.g. 80, 80-90).
        type: str
        required: true
      target_address:
        description: Target IP address.
        type: str
        required: true
      target_port:
        description: Target port(s).
        type: str
        required: false
      description:
        description: Port description.
        type: str
        required: false
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
- name: Create a network forward
  crystian.incus.incus_network_forward:
    network: mynetwork
    listen_address: 192.168.1.50
    description: "Web server forward"
    config:
      target_address: 10.0.0.10
    ports:
      - protocol: tcp
        listen_port: "80"
        target_address: 10.0.0.10
        target_port: "80"
      - protocol: tcp
        listen_port: "443"
        target_address: 10.0.0.10
        target_port: "443"

- name: Delete a network forward
  crystian.incus.incus_network_forward:
    network: mynetwork
    listen_address: 192.168.1.50
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

class IncusNetworkForward(object):
    def __init__(self, module):
        self.module = module
        self.network = module.params['network']
        self.listen_address = module.params['listen_address']
        self.state = module.params['state']
        self.description = module.params['description']
        self.config = module.params['config']
        self.ports = module.params['ports']
        self.project = module.params['project']
        self.remote = module.params['remote']

    def get_network_target(self):
        if self.remote and self.remote != 'local':
            return "{}:{}".format(self.remote, self.network)
        return self.network

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

    def get_forward(self):
        cmd = ['network', 'forward', 'show', self.get_network_target(), self.listen_address]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc == 0:
            try:
                return yaml.safe_load(out)
            except:
                pass
        return None

    def create_or_update(self):
        current = self.get_forward()
        
        desired = {
            'listen_address': self.listen_address,
            'description': self.description if self.description is not None else (current.get('description', '') if current else ''),
            'config': self.config if self.config is not None else (current.get('config', {}) if current else {}),
            'ports': self.ports if self.ports is not None else (current.get('ports', []) if current else [])
        }

        if current:
            changes_needed = False
            
            if self.description is not None and current.get('description') != self.description:
                changes_needed = True
            
            if self.config is not None and current.get('config') != self.config:
                changes_needed = True

            if self.ports is not None:
                current_ports = sorted(current.get('ports', []), key=lambda k: k.get('listen_port', ''))
                desired_ports = sorted(self.ports, key=lambda k: k.get('listen_port', ''))
                
                normalized_current = []
                for p in current_ports:
                    new_p = {}
                    for k in ['protocol', 'listen_port', 'target_address', 'target_port', 'description']:
                        if k in p:
                            new_p[k] = str(p[k])
                    
                    if 'description' not in new_p:
                        new_p['description'] = ''
                    if 'target_port' not in new_p and 'listen_port' in new_p:
                         new_p['target_port'] = new_p['listen_port']

                    normalized_current.append(new_p)

                normalized_desired = []
                for p in desired_ports:
                     new_p = {}
                     for k in ['protocol', 'listen_port', 'target_address', 'target_port', 'description']:
                        if k in p and p[k] is not None:
                            new_p[k] = str(p[k])
                     
                     if 'description' not in new_p:
                        new_p['description'] = ''
                     if 'target_port' not in new_p and 'listen_port' in new_p:
                        new_p['target_port'] = new_p['listen_port']
                     
                     normalized_desired.append(new_p)

                if normalized_current != normalized_desired:
                    changes_needed = True 


            if not changes_needed:
                self.module.exit_json(changed=False, msg="Network forward matches configuration")

            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Network forward would be updated")

            rc, out, err = self.run_incus(
                ['network', 'forward', 'edit', self.get_network_target(), self.listen_address], 
                stdin=yaml.dump(desired)
            )
            if rc != 0:
                self.module.fail_json(msg="Failed to update network forward: " + err, stdout=out, stderr=err)
            
            self.module.exit_json(changed=True, msg="Network forward updated")

        else:
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Network forward would be created")
            
            cmd = ['network', 'forward', 'create', self.get_network_target(), self.listen_address]
            rc, out, err = self.run_incus(cmd)
            if rc != 0:
                self.module.fail_json(msg="Failed to create network forward: " + err, stdout=out, stderr=err)
            
            rc, out, err = self.run_incus(
                ['network', 'forward', 'edit', self.get_network_target(), self.listen_address], 
                stdin=yaml.dump(desired)
            )
            if rc != 0:
                 self.run_incus(['network', 'forward', 'delete', self.get_network_target(), self.listen_address], check_rc=False)
                 self.module.fail_json(msg="Failed to configure created network forward: " + err, stdout=out, stderr=err)

            self.module.exit_json(changed=True, msg="Network forward created")

    def delete(self):
        if self.module.check_mode:
             if self.get_forward():
                self.module.exit_json(changed=True, msg="Network forward would be deleted")
             else:
                self.module.exit_json(changed=False, msg="Network forward already absent")

        if not self.get_forward():
            self.module.exit_json(changed=False, msg="Network forward already absent")

        cmd = ['network', 'forward', 'delete', self.get_network_target(), self.listen_address]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
             self.module.fail_json(msg="Failed to delete network forward: " + err, stdout=out, stderr=err)
        
        self.module.exit_json(changed=True, msg="Network forward deleted")

    def run(self):
        if self.state == 'present':
            self.create_or_update()
        elif self.state == 'absent':
            self.delete()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            network=dict(type='str', required=True),
            listen_address=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            description=dict(type='str', required=False),
            config=dict(type='dict', required=False),
            ports=dict(type='list', elements='dict', required=False, options=dict(
                protocol=dict(type='str', required=True, choices=['tcp', 'udp']),
                listen_port=dict(type='str', required=True),
                target_address=dict(type='str', required=True),
                target_port=dict(type='str', required=False),
                description=dict(type='str', required=False),
            )),
            project=dict(type='str', default='default', required=False),
            remote=dict(type='str', default='local', required=False),
        ),
        supports_check_mode=True,
    )

    manager = IncusNetworkForward(module)
    manager.run()

if __name__ == '__main__':
    main()
