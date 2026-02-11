#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: incus_query
  author: Crystian @Crystian0704
  version_added: "1.0.0"
  short_description: Query Incus API
  description:
      - This lookup performs a raw query against the Incus API.
      - Useful for retrieving information not covered by specific lookups.
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
- name: Get project info
  debug:
    msg: "{{ lookup('crystian.incus.incus_query', '/1.0/projects/default') }}"
"""

RETURN = r"""
  _raw:
    description: API response (parsed JSON)
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
            api_path = term
            
            if '?' in api_path:
                if project:
                     api_path += "&project=%s" % project
            else:
                if project:
                     api_path += "?project=%s" % project
            
            cmd = ['incus', 'query', api_path]
                
            if remote and remote != 'local':
                 cmd[2] = "%s:%s" % (remote, api_path)
            
            env = os.environ.copy()
            env['LC_ALL'] = 'C'
            
            try:
                display.vvvv(u"Incus query lookup running: %s" % " ".join(cmd))
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
                stdout, stderr = p.communicate()
                
                if p.returncode != 0:
                     try:
                         ret.append(json.loads(stdout.decode('utf-8')))
                         continue
                     except:
                        raise AnsibleError("Error querying incus API %s: %s" % (api_path, stderr.decode('utf-8')))
                
                if not stdout:
                     ret.append(None)
                     continue

                try:
                    ret.append(json.loads(stdout.decode('utf-8')))
                except ValueError:
                    ret.append(stdout.decode('utf-8'))
                
            except Exception as e:
                raise AnsibleError("Failed to query incus API: %s" % str(e))
                
        return ret
