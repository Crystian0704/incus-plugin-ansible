#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: incus_admin_init
  module: incus_admin_init
  author: Crystian @Crystian0704
  version_added: "1.0.0"
  short_description: Initialize Incus server
  description:
      - Initialize an Incus server using a YAML preseed configuration.
      - Wraps 'incus admin init --preseed'.
      - Idempotency is handled by checking if the server seems initialized (e.g. has storage pools).
  options:
    config:
      description:
        - The preseed configuration as a dictionary.
        - Structure should match the YAML format expected by 'incus admin init --preseed'.
      required: true
      type: dict
    remote:
      description:
        - The remote Incus server to initialize.
        - Defaults to 'local'.
      required: False
      type: string
    force:
      description:
        - Force initialization even if the server appears to be already initialized.
        - WARNING: This may fail if resources already exist or cause data loss depending on the config.
      type: bool
      default: false
"""

EXAMPLES = r"""
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

"""

RETURN = r"""
  # Standard Ansible return values
"""

from ansible.module_utils.basic import AnsibleModule
import json
import subprocess
import yaml

class IncusAdminInit(object):
    def __init__(self, module):
        self.module = module
        self.config = module.params['config']
        self.remote = module.params['remote']
        self.force = module.params['force']
        self.minimal = module.params['minimal']
        self.incus_path = module.get_bin_path('incus', required=True)

    def _run_command(self, cmd, stdin=None, check_rc=True):
        try:
            stdin_bytes = None
            if stdin:
                stdin_bytes = stdin.encode('utf-8')
            
            rc, out, err = self.module.run_command(cmd, data=stdin, check_rc=check_rc)
            return rc, out, err
        except Exception as e:
            self.module.fail_json(msg="Failed to run command: {}".format(e))

    def is_initialized(self):
        cmd = [self.incus_path, 'storage', 'list', '--format=json']
        if self.remote and self.remote != 'local':
             cmd.append("{}:".format(self.remote))
             
        rc, out, err = self._run_command(cmd, check_rc=False)
        
        if rc == 0:
            try:
                pools = json.loads(out)
                if len(pools) > 0:
                    return True
            except ValueError:
                pass
        
        return False

    def run(self):
        if not self.force and self.is_initialized():
             self.module.exit_json(changed=False, msg="Incus appears to be already initialized (storage pools found). Use force=true to override.")

        if self.module.check_mode:
             self.module.exit_json(changed=True, msg="Incus would be initialized with provided preseed.")

        cmd = [self.incus_path, 'admin', 'init', '--preseed']
        if self.remote and self.remote != 'local':
             cmd.append("{}:".format(self.remote))
        
        preseed_yaml = yaml.dump(self.config)
        
        rc, out, err = self._run_command(cmd, stdin=preseed_yaml, check_rc=True)
        
        self.module.exit_json(changed=True, msg="Incus initialized successfully", stdout=out, stderr=err)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            config=dict(type='dict', required=False),
            remote=dict(type='str', required=False),
            force=dict(type='bool', default=False),
            minimal=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )

    initializer = IncusAdminInit(module)
    initializer.run()

if __name__ == '__main__':
    main()
