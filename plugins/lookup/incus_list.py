#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: incus_list
  author: Crystian @Crystian0704
  version_added: "1.0.0"
  short_description: List Incus instances
  description:
      - This lookup returns a list of Incus instances, similar to 'incus list'.
      - It returns a list of dictionaries, where each dictionary represents an instance.
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
    filters:
        description:
            - List of filters to apply (e.g. 'status=RUNNING', 'type=container').
        required: False
        type: list
        elements: string
    all_projects:
       description:
         - If true, list instances from all projects.
       required: False
       type: boolean
       default: False
"""

EXAMPLES = r"""
- name: List all running containers
  debug:
    msg: "{{ lookup('crystian.incus.incus_list', filters=['status=RUNNING', 'type=container']) }}"

- name: List all instances on a remote
  debug:
    msg: "{{ lookup('crystian.incus.incus_list', remote='myremote') }}"
"""

RETURN = r"""
  _list:
    description: List of instance dictionaries
    type: list
"""

from ansible.errors import AnsibleError, AnsibleParserError
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
        filters = self.get_option('filters') or []
        all_projects = self.get_option('all_projects')

        # If terms are provided, treat them as filters (backwards compatibility/convenience)
        # But standard way is kwargs usually for complex lookups.
        # Let's append terms to filters if compatible.
        for term in terms:
            if isinstance(term, str):
                filters.append(term)
        
        cmd = ['incus', 'list', '--format=json']

        target = remote + ":" if remote and remote != 'local' else ''
        
        # filters are positional arguments in incus list
        # incus list [remote:] [filters]
        
        # If we have filters, we add them. 
        # Note: if remote is specified, it is usually part of the first argument if it isn't a filter.
        # incus list myremote: type=container
        
        cmd_args = []
        if target:
             # We need to be careful. If target is just "remote:", incus list expects it.
             cmd_args.append(target)
        
        # Append filters
        cmd_args.extend(filters)
        
        cmd.extend(cmd_args)

        if all_projects:
            cmd.append('--all-projects')
        elif project:
            cmd.extend(['--project', project])

        env = os.environ.copy()
        env['LC_ALL'] = 'C'

        try:
            display.vvvv(u"Incus list lookup running: %s" % " ".join(cmd))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            stdout, stderr = p.communicate()
            
            if p.returncode != 0:
                raise AnsibleError("Error running incus list: %s" % stderr.decode('utf-8'))
            
            return json.loads(stdout.decode('utf-8'))

        except Exception as e:
            raise AnsibleError("Failed to lookup incus instances: %s" % str(e))
