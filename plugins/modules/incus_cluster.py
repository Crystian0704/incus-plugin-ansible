#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: incus_cluster
short_description: Manage Incus clusters
description:
  - Enable clustering on a standalone server.
  - Generate join tokens for new members.
  - List and show cluster members.
  - Configure cluster member settings.
  - Manage cluster groups (create, assign, delete, list).
  - Remove members from the cluster.
version_added: "1.2.0"
options:
  name:
    description:
      - Name of the cluster member.
      - Required for C(state=enabled), C(state=present), C(state=absent).
      - Not required for C(state=listed).
    required: false
    type: str
  state:
    description:
      - Desired state of the cluster member or operation.
      - C(enabled) enables clustering on a standalone server, turning it into the first member.
      - C(present) generates a join token for a new member to join the cluster.
      - C(absent) removes a member from the cluster.
      - C(listed) lists all cluster members (returns member list in C(members)).
    required: false
    type: str
    choices: [ enabled, present, absent, listed ]
    default: present
  config:
    description:
      - Dictionary of configuration options to set on the cluster member.
      - Uses C(incus cluster set <member> key=value).
      - Only used with C(state=present) when the member already exists.
    required: false
    type: dict
  groups:
    description:
      - Manage cluster groups.
      - "When C(state=present): a list of dicts with C(name) and optional C(description) creates groups."
      - "When C(state=present) and C(name) is set: a list of strings assigns groups to the member."
      - "When C(state=absent): a list of strings deletes groups."
      - "When C(state=listed) and C(groups=true): lists all cluster groups."
    required: false
    type: raw
  force:
    description:
      - Force removal of a degraded member.
      - Only used with C(state=absent).
    required: false
    type: bool
    default: false
  remote:
    description:
      - The remote Incus server to target.
      - Defaults to 'local'.
    required: false
    type: str
    default: local
  project:
    description:
      - The project context.
    required: false
    type: str
author:
  - Crystian @Crystian0704
'''

EXAMPLES = r'''
- name: Enable clustering on a standalone server
  crystian.incus.incus_cluster:
    name: node1
    state: enabled

- name: Generate a join token for a new member
  crystian.incus.incus_cluster:
    name: node2
    state: present
  register: join_result

- name: Show join token
  debug:
    msg: "Join token: {{ join_result.token }}"

- name: List cluster members
  crystian.incus.incus_cluster:
    state: listed
  register: cluster_info

- name: Set cluster member config
  crystian.incus.incus_cluster:
    name: node1
    config:
      scheduler.instance: all
    state: present

- name: Create cluster groups
  crystian.incus.incus_cluster:
    groups:
      - name: compute
        description: "Compute nodes"
      - name: storage
        description: "Storage nodes"
    state: present

- name: Assign groups to a member
  crystian.incus.incus_cluster:
    name: node1
    groups:
      - compute
      - storage
    state: present

- name: List cluster groups
  crystian.incus.incus_cluster:
    groups: true
    state: listed

- name: Delete cluster groups
  crystian.incus.incus_cluster:
    groups:
      - compute
    state: absent

- name: Remove a member from the cluster
  crystian.incus.incus_cluster:
    name: node3
    state: absent
    force: true
'''

RETURN = r'''
msg:
  description: Status message.
  returned: always
  type: str
token:
  description: Join token generated for a new member.
  returned: when state=present and a join token is generated
  type: str
members:
  description: List of cluster members.
  returned: when state=listed and groups is not set
  type: list
groups:
  description: List of cluster groups.
  returned: when state=listed and groups=true
  type: list
member:
  description: Details of a specific cluster member.
  returned: when state=present and member already exists
  type: dict
'''

from ansible.module_utils.basic import AnsibleModule
import json
import os
import subprocess
import yaml


class IncusCluster(object):
    def __init__(self, module):
        self.module = module
        self.name = module.params['name']
        self.state = module.params['state']
        self.config = module.params['config']
        self.groups = module.params['groups']
        self.force = module.params['force']
        self.remote = module.params['remote']
        self.project = module.params['project']

    def get_target_name(self, name=None):
        n = name or self.name
        if self.remote and self.remote != 'local':
            return "{}:{}".format(self.remote, n)
        return n

    def get_target_remote(self):
        if self.remote and self.remote != 'local':
            return "{}:".format(self.remote)
        return None

    def run_incus(self, args, check_rc=True):
        cmd = ['incus']
        if self.project:
            cmd.extend(['--project', self.project])
        cmd.extend(args)

        env = os.environ.copy()
        env['LC_ALL'] = 'C'

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=env
        )
        stdout, stderr = p.communicate()

        if check_rc and p.returncode != 0:
            return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

        return p.returncode, stdout.decode('utf-8'), stderr.decode('utf-8')

    def get_members(self):
        cmd = ['cluster', 'list', '--format=json']
        remote = self.get_target_remote()
        if remote:
            cmd.append(remote)

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc == 0:
            try:
                return json.loads(out)
            except (ValueError, TypeError):
                pass
        return []

    def get_member(self, name=None):
        target = self.get_target_name(name)
        cmd = ['cluster', 'show', target]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc == 0:
            try:
                return yaml.safe_load(out)
            except Exception:
                pass
        return None

    def is_clustered(self):
        members = self.get_members()
        return len(members) > 0

    def enable(self):
        if self.is_clustered():
            self.module.exit_json(
                changed=False,
                msg="Clustering is already enabled"
            )

        if self.module.check_mode:
            self.module.exit_json(changed=True, msg="Clustering would be enabled")

        target = self.get_target_name()
        cmd = ['cluster', 'enable', target]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
            self.module.fail_json(
                msg="Failed to enable clustering: " + err,
                stdout=out, stderr=err
            )

        self.module.exit_json(changed=True, msg="Clustering enabled")

    def add(self):
        if self.module.check_mode:
            self.module.exit_json(changed=True, msg="Join token would be generated")

        target = self.get_target_name()
        cmd = ['cluster', 'add', target]
        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
            self.module.fail_json(
                msg="Failed to generate join token: " + err,
                stdout=out, stderr=err
            )

        token = out.strip()
        if token.startswith("Member "):
            lines = token.split('\n')
            token = lines[-1].strip() if len(lines) > 1 else token

        self.module.exit_json(
            changed=True,
            msg="Join token generated",
            token=token
        )

    def remove(self):
        member = self.get_member()
        if not member:
            self.module.exit_json(changed=False, msg="Member not found in cluster")

        if self.module.check_mode:
            self.module.exit_json(changed=True, msg="Member would be removed")

        target = self.get_target_name()
        cmd = ['cluster', 'remove', target]
        if self.force:
            cmd.extend(['--force', '--yes'])

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
            self.module.fail_json(
                msg="Failed to remove member: " + err,
                stdout=out, stderr=err
            )

        self.module.exit_json(changed=True, msg="Member removed from cluster")

    def list_members(self):
        members = self.get_members()
        self.module.exit_json(
            changed=False,
            msg="Cluster members listed",
            members=members
        )

    def set_config(self):
        if not self.config:
            return False

        member = self.get_member()
        if not member:
            self.module.fail_json(msg="Member '{}' not found in cluster".format(self.name))

        current_config = member.get('config', {})
        changed = False
        to_set = {}

        for key, value in self.config.items():
            str_v = str(value).lower() if isinstance(value, bool) else str(value)
            if key not in current_config or str(current_config.get(key, '')) != str_v:
                to_set[key] = str_v

        if to_set:
            if self.module.check_mode:
                return True

            target = self.get_target_name()
            cmd = ['cluster', 'set', target]
            for k, v in to_set.items():
                cmd.append("{}={}".format(k, v))

            rc, out, err = self.run_incus(cmd, check_rc=False)
            if rc != 0:
                self.module.fail_json(
                    msg="Failed to set config: " + err,
                    stdout=out, stderr=err
                )
            changed = True

        return changed

    def get_groups(self):
        cmd = ['cluster', 'group', 'list', '--format=json']
        remote = self.get_target_remote()
        if remote:
            cmd.append(remote)

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc == 0:
            try:
                return json.loads(out)
            except (ValueError, TypeError):
                pass
        return []

    def list_groups(self):
        groups = self.get_groups()
        self.module.exit_json(
            changed=False,
            msg="Cluster groups listed",
            groups=groups
        )

    def create_groups(self):
        if not isinstance(self.groups, list):
            self.module.fail_json(msg="'groups' must be a list for creation")

        existing = self.get_groups()
        existing_names = [g.get('name', '') for g in existing]
        changed = False

        for group in self.groups:
            if not isinstance(group, dict) or 'name' not in group:
                continue

            group_name = group['name']
            if group_name in existing_names:
                continue

            if self.module.check_mode:
                changed = True
                continue

            target = self.get_target_name(group_name)
            cmd = ['cluster', 'group', 'create', target]
            desc = group.get('description')
            if desc:
                cmd.extend(['--description', desc])

            rc, out, err = self.run_incus(cmd, check_rc=False)
            if rc != 0:
                self.module.fail_json(
                    msg="Failed to create group '{}': {}".format(group_name, err),
                    stdout=out, stderr=err
                )
            changed = True

        return changed

    def assign_groups(self):
        if not isinstance(self.groups, list) or not self.name:
            self.module.fail_json(msg="'name' and 'groups' (list of strings) are required for assign")

        member = self.get_member()
        if not member:
            self.module.fail_json(msg="Member '{}' not found in cluster".format(self.name))

        current_groups = member.get('groups', [])
        if current_groups is None:
            current_groups = []

        target_groups = sorted(self.groups)
        current_sorted = sorted(current_groups)

        if target_groups == current_sorted:
            return False

        if self.module.check_mode:
            return True

        target = self.get_target_name()
        groups_str = ','.join(self.groups)
        cmd = ['cluster', 'group', 'assign', target, groups_str]

        rc, out, err = self.run_incus(cmd, check_rc=False)
        if rc != 0:
            self.module.fail_json(
                msg="Failed to assign groups: " + err,
                stdout=out, stderr=err
            )
        return True

    def delete_groups(self):
        if not isinstance(self.groups, list):
            self.module.fail_json(msg="'groups' must be a list of strings for deletion")

        existing = self.get_groups()
        existing_names = [g.get('name', '') for g in existing]
        changed = False

        for group_name in self.groups:
            if not isinstance(group_name, str):
                continue
            if group_name not in existing_names:
                continue

            if self.module.check_mode:
                changed = True
                continue

            target = self.get_target_name(group_name)
            cmd = ['cluster', 'group', 'delete', target]

            rc, out, err = self.run_incus(cmd, check_rc=False)
            if rc != 0:
                self.module.fail_json(
                    msg="Failed to delete group '{}': {}".format(group_name, err),
                    stdout=out, stderr=err
                )
            changed = True

        return changed

    def handle_present(self):
        if self.groups:
            if isinstance(self.groups, list) and len(self.groups) > 0:
                if isinstance(self.groups[0], dict):
                    changed = self.create_groups()
                    if self.name:
                        changed_config = self.set_config()
                        changed = changed or changed_config
                    self.module.exit_json(changed=changed, msg="Groups processed")
                elif isinstance(self.groups[0], str):
                    if self.name:
                        changed_assign = self.assign_groups()
                        changed_config = self.set_config()
                        changed = changed_assign or changed_config
                        member = self.get_member()
                        self.module.exit_json(
                            changed=changed,
                            msg="Groups assigned" if changed_assign else "Member matches configuration",
                            member=member
                        )
                    else:
                        self.module.fail_json(msg="'name' is required to assign groups to a member")

        if self.name:
            member = self.get_member()
            if member:
                changed = self.set_config()
                self.module.exit_json(
                    changed=changed,
                    msg="Member configuration updated" if changed else "Member matches configuration",
                    member=member
                )
            else:
                self.add()
        else:
            self.module.fail_json(msg="'name' is required for state=present")

    def handle_absent(self):
        if self.groups:
            changed = self.delete_groups()
            self.module.exit_json(
                changed=changed,
                msg="Groups deleted" if changed else "Groups already absent"
            )
        else:
            if not self.name:
                self.module.fail_json(msg="'name' is required for state=absent without groups")
            self.remove()

    def handle_listed(self):
        if self.groups and self.groups is True:
            self.list_groups()
        elif self.groups:
            self.list_groups()
        else:
            self.list_members()

    def run(self):
        if self.state == 'enabled':
            if not self.name:
                self.module.fail_json(msg="'name' is required for state=enabled")
            self.enable()
        elif self.state == 'present':
            self.handle_present()
        elif self.state == 'absent':
            self.handle_absent()
        elif self.state == 'listed':
            self.handle_listed()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=False),
            state=dict(type='str', default='present',
                       choices=['enabled', 'present', 'absent', 'listed']),
            config=dict(type='dict', required=False),
            groups=dict(type='raw', required=False),
            force=dict(type='bool', default=False),
            remote=dict(type='str', default='local', required=False),
            project=dict(type='str', required=False),
        ),
        supports_check_mode=True,
    )

    manager = IncusCluster(module)
    manager.run()


if __name__ == '__main__':
    main()
