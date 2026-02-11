#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: incus_info
  author: Crystian @Crystian0704
  version_added: "1.0.0"
  short_description: Get Incus instance info and state
  description:
      - This lookup returns the full information of an Incus instance, including runtime state.
      - It combines 'incus query /1.0/instances/<instance>' and 'incus query /1.0/instances/<instance>/state'.
  options:
    remote:
      description:
        - The remote Incus server to query.
        - Defaults to 'local'.
      required: False
      type: string
      default: local
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
  debug:
    msg: "{{ lookup('crystian.incus.incus_info', 'my-container') }}"
"""

RETURN = r"""
  _raw:
    description: Instance info dictionary (config + state)
    type: dict
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import subprocess
import json
import os

display = Display()

class LookupModule(LookupBase):

    def _query(self, remote, project, path):
        if project:
             path += "?project=%s" % project

        cmd = ['incus', 'query', path]
        
        if remote and remote != 'local':
             cmd[2] = "%s:%s" % (remote, path)

        env = os.environ.copy()
        env['LC_ALL'] = 'C'
        
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        stdout, stderr = p.communicate()
        
        if p.returncode != 0:
            raise AnsibleError("Error querying incus path %s: %s" % (path, stderr.decode('utf-8')))
        
        return json.loads(stdout.decode('utf-8'))

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        
        remote = self.get_option('remote')
        project = self.get_option('project')
        
        ret = []
        
        for term in terms:
            instance_name = term
            
            try:
                config = self._query(remote, project, "/1.0/instances/%s" % instance_name)
                
                state = self._query(remote, project, "/1.0/instances/%s/state" % instance_name)
                
                config['state_info'] = state
                
                ret.append(config)
                
            except Exception as e:
                raise AnsibleError("Failed to lookup incus info for %s: %s" % (instance_name, str(e)))
                
        return ret
