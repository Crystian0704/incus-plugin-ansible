#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: incus_config
  author: Crystian @Crystian0704
  version_added: "1.0.0"
  short_description: Get Incus instance configuration
  description:
      - This lookup returns the configuration of an Incus instance.
      - It wraps 'incus query /1.0/instances/<instance>'.
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
- name: Get config for an instance
  debug:
    msg: "{{ lookup('crystian.incus.incus_config', 'my-container') }}"
"""

RETURN = r"""
  _raw:
    description: Instance configuration dictionary
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

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        
        remote = self.get_option('remote')
        project = self.get_option('project')
        
        ret = []
        
        for term in terms:
            # Term is the instance name
            instance_name = term
            
            api_path = "/1.0/instances/%s" % instance_name
            
            cmd = ['incus', 'query', api_path]
            
            if project:
                cmd.extend(['--project', project])
                
            # For remote, incus query [remote:]/1.0/instances/...
            if remote and remote != 'local':
                 cmd[2] = "%s:%s" % (remote, api_path)
            
            env = os.environ.copy()
            env['LC_ALL'] = 'C'
            
            try:
                display.vvvv(u"Incus config lookup running: %s" % " ".join(cmd))
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                stdout, stderr = p.communicate()
                
                if p.returncode != 0:
                     # If not found or other error, maybe return None or fail?
                     # Standard lookup behavior is to fail if strict, or maybe return empty?
                     # Let's raise error for now as it's explicit.
                    raise AnsibleError("Error fetching incus config for %s: %s" % (instance_name, stderr.decode('utf-8')))
                
                ret.append(json.loads(stdout.decode('utf-8')))
                
            except Exception as e:
                raise AnsibleError("Failed to lookup incus config: %s" % str(e))
                
        return ret
