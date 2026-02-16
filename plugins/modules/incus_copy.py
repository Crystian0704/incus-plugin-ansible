#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = r'''
---
module: incus_copy
short_description: Copy or move Incus instances
description:
  - Copy or move Incus instances within or between servers.
  - Supports local and cross-server operations.
version_added: "1.0.0"
options:
  source:
    description:
      - Source instance name (or remote:name for cross-server).
    required: true
    type: str
  dest:
    description:
      - Destination instance name (or remote:name for cross-server).
    required: true
    type: str
  move:
    description:
      - If true, move the instance instead of copying.
      - The source instance will be deleted after transfer.
    type: bool
    default: false
  instance_only:
    description:
      - Copy/move the instance without its snapshots.
    type: bool
    default: false
  mode:
    description:
      - Transfer mode for cross-server operations.
    type: str
    choices: ['pull', 'push', 'relay']
    default: pull
  storage:
    description:
      - Target storage pool for the copied/moved instance.
    type: str
    required: false
  profiles:
    description:
      - List of profiles to apply to the new instance.
    type: list
    elements: str
    required: false
  no_profiles:
    description:
      - Create the instance with no profiles applied.
    type: bool
    default: false
  ephemeral:
    description:
      - Make the copied instance ephemeral.
    type: bool
    default: false
  project:
    description:
      - Project to use.
    type: str
    default: default
    required: false
  remote:
    description:
      - Remote server context (applied to both source and dest if they don't contain a colon).
    type: str
    default: local
    required: false
author:
  - Crystian @Crystian0704
'''
EXAMPLES = r'''
- name: Copy an instance locally
  crystian.incus.incus_copy:
    source: my-instance
    dest: my-instance-copy

- name: Move an instance (rename)
  crystian.incus.incus_copy:
    source: old-name
    dest: new-name
    move: true

- name: Copy without snapshots
  crystian.incus.incus_copy:
    source: my-instance
    dest: my-instance-copy
    instance_only: true

- name: Copy to a different storage pool
  crystian.incus.incus_copy:
    source: my-instance
    dest: my-instance-copy
    storage: fast-pool

- name: Copy across servers
  crystian.incus.incus_copy:
    source: local:my-instance
    dest: remote-server:my-instance
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

class IncusCopy(object):
    def __init__(self, module):
        self.module = module
        self.source = module.params['source']
        self.dest = module.params['dest']
        self.move = module.params['move']
        self.instance_only = module.params['instance_only']
        self.mode = module.params['mode']
        self.storage = module.params['storage']
        self.profiles = module.params['profiles']
        self.no_profiles = module.params['no_profiles']
        self.ephemeral = module.params['ephemeral']
        self.project = module.params['project']
        self.remote = module.params['remote']
        self.incus_path = module.get_bin_path('incus', required=True)

    def _format_name(self, name):
        if ':' in name:
            return name
        if self.remote and self.remote != 'local':
            return '{}:{}'.format(self.remote, name)
        return name

    def _run_command(self, cmd, check_rc=True):
        if self.project and self.project != 'default':
            if '--project' not in cmd:
                cmd.insert(1, self.project)
                cmd.insert(1, '--project')
        try:
            rc, out, err = self.module.run_command(cmd, check_rc=check_rc)
            if check_rc and rc != 0:
                self.module.fail_json(msg="Command execution failed", cmd=cmd, rc=rc, stdout=out, stderr=err)
            return rc, out, err
        except Exception as e:
            self.module.fail_json(msg="Command execution exception: %s" % str(e), cmd=cmd)

    def instance_exists(self, name):
        formatted = self._format_name(name)
        if ':' in formatted:
            parts = formatted.split(':', 1)
            prefix = parts[0] + ':'
            instance_name = parts[1]
        else:
            prefix = ''
            instance_name = formatted
        cmd = [self.incus_path, 'list', '--format=json', '{}^{}$'.format(prefix, instance_name)]
        rc, out, err = self._run_command(cmd, check_rc=False)
        if rc == 0:
            try:
                data = json.loads(out)
                return len(data) > 0
            except ValueError:
                pass
        return False

    def copy_instance(self):
        source = self._format_name(self.source)
        dest = self._format_name(self.dest)
        cmd = [self.incus_path, 'copy', source, dest]
        if self.instance_only:
            cmd.append('--instance-only')
        if self.mode and self.mode != 'pull':
            cmd.extend(['--mode', self.mode])
        if self.storage:
            cmd.extend(['--storage', self.storage])
        if self.no_profiles:
            cmd.append('--no-profiles')
        elif self.profiles:
            for p in self.profiles:
                cmd.extend(['--profile', p])
        if self.ephemeral:
            cmd.append('--ephemeral')
        self._run_command(cmd)

    def move_instance(self):
        source = self._format_name(self.source)
        dest = self._format_name(self.dest)
        cmd = [self.incus_path, 'move', source, dest]
        if self.instance_only:
            cmd.append('--instance-only')
        if self.mode and self.mode != 'pull':
            cmd.extend(['--mode', self.mode])
        if self.storage:
            cmd.extend(['--storage', self.storage])
        self._run_command(cmd)

    def run(self):
        source_exists = self.instance_exists(self.source)
        dest_exists = self.instance_exists(self.dest)

        if self.move:
            if not source_exists and dest_exists:
                self.module.exit_json(changed=False, msg="Instance already moved")
            if not source_exists and not dest_exists:
                self.module.fail_json(msg="Source instance '{}' not found".format(self.source))
            if dest_exists:
                self.module.fail_json(msg="Cannot move: destination '{}' already exists".format(self.dest))
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Instance would be moved")
            self.move_instance()
            self.module.exit_json(changed=True, msg="Instance moved")
        else:
            if dest_exists:
                self.module.exit_json(changed=False, msg="Destination instance already exists")
            if not source_exists:
                self.module.fail_json(msg="Source instance '{}' not found".format(self.source))
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg="Instance would be copied")
            self.copy_instance()
            self.module.exit_json(changed=True, msg="Instance copied")

def main():
    module = AnsibleModule(
        argument_spec=dict(
            source=dict(type='str', required=True),
            dest=dict(type='str', required=True),
            move=dict(type='bool', default=False),
            instance_only=dict(type='bool', default=False),
            mode=dict(type='str', choices=['pull', 'push', 'relay'], default='pull'),
            storage=dict(type='str', required=False),
            profiles=dict(type='list', elements='str', required=False),
            no_profiles=dict(type='bool', default=False),
            ephemeral=dict(type='bool', default=False),
            project=dict(type='str', default='default', required=False),
            remote=dict(type='str', default='local', required=False),
        ),
        supports_check_mode=True,
    )
    manager = IncusCopy(module)
    manager.run()

if __name__ == '__main__':
    main()
