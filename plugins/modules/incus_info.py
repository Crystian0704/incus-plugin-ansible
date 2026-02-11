#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: incus_info
  module: incus_info
  author: Crystian @Crystian0704
  version_added: "1.0.0"
  short_description: Get Incus instance info and state
  description:
      - This module returns the full information of an Incus instance, including runtime state.
      - It combines 'incus query /1.0/instances/<instance>' and 'incus query /1.0/instances/<instance>/state'.
      - Useful for gathering facts about an instance on a remote host.
  options:
    name:
      description:
        - Name of the instance.
      required: true
      type: str
    remote:
      description:
        - The remote Incus server to query.
        - Defaults to 'local'.
      required: False
      type: string
    project:
      description:
        - The project to query.
        - Defaults to 'default'.
      required: False
      type: string
      default: default
"""

EXAMPLES = r"""
- name: Get info for an instance
  crystian.incus.incus_info:
    name: my-container
  register: instance_info

- name: Debug info
  debug:
    var: instance_info.info
"""

RETURN = r"""
  info:
    description: Instance info dictionary (config + state)
    type: dict
    returned: always
"""

from ansible.module_utils.basic import AnsibleModule
import json
import subprocess
import os

class IncusInfo(object):
    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.remote = module.params['remote']
        self.project = module.params['project']
        self.incus_path = module.get_bin_path('incus', required=True)

    def _run_command(self, cmd, check_rc=True):
        try:
            rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
            return rc, out, err
        except Exception as e:
            self.module.fail_json(msg="Failed to run command: {}".format(e))

    def _query(self, path):
        full_path = path
        if self.project:
            full_path += "?project=%s" % self.project

        cmd = [self.incus_path, 'query', full_path]
        
        if self.remote and self.remote != 'local':
             cmd[2] = "%s:%s" % (self.remote, full_path)

        rc, out, err = self._run_command(cmd)
        
        if rc != 0:
            self.module.fail_json(msg="Error querying incus path %s: %s" % (path, err))
        
        try:
            return json.loads(out)
        except ValueError:
            self.module.fail_json(msg="Failed to parse JSON output from query", stdout=out)

    def run(self):
        try:
            if not self.name:
                info = self._query("/1.0")
                self.module.exit_json(changed=False, info=info)
                return

            config = self._query("/1.0/instances/%s" % self.name)
            
            state = self._query("/1.0/instances/%s/state" % self.name)
            
            config['state_info'] = state
            
            self.module.exit_json(changed=False, info=config)
            
        except Exception as e:
            self.module.fail_json(msg="Failed to get instance info: %s" % str(e))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=False),
            remote=dict(type='str', required=False),
            project=dict(type='str', required=False, default='default'),
        ),
        supports_check_mode=True,
    )

    info_module = IncusInfo(module)
    info_module.run()

if __name__ == '__main__':
    main()
