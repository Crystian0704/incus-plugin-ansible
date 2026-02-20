from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: incus_inventory
    plugin_type: inventory
    short_description: Incus inventory source
    description:
        - Get instances from Incus to be used as an inventory source.
        - Supports grouping by remote, project, and instance tags.
        - Automatically sets connection variables for the `community.general.incus` connection plugin (`ansible_connection`, `ansible_incus_remote`, `ansible_incus_project`, `ansible_host`).
        - Retrieves all instance settings into `incus_config_*` specific variables, allowing advanced dynamic grouping.
        - Provides tag dictionaries in `incus_user_tags` object automatically extracted from user.* properties.
    options:
        plugin:
            description: Token that ensures this is a source file for the 'incus_inventory' plugin.
            required: True
            choices: ['crystian.incus.incus_inventory']
        remotes:
            description:
                - List of Incus remotes to search for instances.
            default: ['local']
            type: list
            elements: str
            env:
                - name: INCUS_INVENTORY_REMOTES
        projects:
            description:
                - List of Incus projects to search for instances.
            default: ['default']
            type: list
            elements: str
            env:
                - name: INCUS_INVENTORY_PROJECTS
        tags:
            description:
                - Filter instances by tags (user.<key>=<value>).
            type: dict
            default: {}
            env:
                - name: INCUS_INVENTORY_TAGS
        running_only:
            description:
                - If true, only return running instances.
            default: False
            type: bool
    extends_documentation_fragment:
        - constructed
        - inventory_cache
    requirements:
        - incus command line tool
'''

EXAMPLES = r'''
# Basic usage
plugin: crystian.incus.incus_inventory
remotes:
  - local
projects:
  - default
  - mywebproject

# Group by tags
plugin: crystian.incus.incus_inventory
keyed_groups:
  - prefix: tag
    key: incus_user_tags

# Filter by tags
plugin: crystian.incus.incus_inventory
tags:
  env: prod

# Group by OS and architecture
plugin: crystian.incus.incus_inventory
keyed_groups:
  - prefix: os
    key: incus_config_image_os
  - prefix: arch
    key: incus_config_image_architecture

# Custom groups with conditions and Jinja2 conditionals
plugin: crystian.incus.incus_inventory
groups:
  webservers: "'web' == tag_service"
  production_db: "'prod' == tag_env and 'db' == tag_role"
  high_performance: "incus_config_limits_cpu | default('1') | int >= 4"
  alpine_servers: "incus_config_image_os == 'Alpine'"

# Setting variables with compose (changing ssh users based on OS image)
plugin: crystian.incus.incus_inventory
compose:
  ansible_user: "'ubuntu' if incus_config_image_os == 'ubuntu' else 'root'"
  ansible_host: "incus_config_user_internal_ip | default(ansible_host)"
  deploy_type: "'kubernetes' if 'k8s_node' in incus_user_tags else 'swarm'"

# Using Cache to speed up execution
plugin: crystian.incus.incus_inventory
remotes:
  - local
cache: yes
cache_plugin: jsonfile
cache_timeout: 3600
cache_connection: /tmp/incus_inventory_cache
'''

import json
import subprocess
import os
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = 'crystian.incus.incus_inventory'

    def verify_file(self, path):
        '''Return true/false if this is possibly a valid file for this plugin to consume'''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('incus_inventory.yml', 'incus_inventory.yaml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        '''Parse the inventory source'''
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        self._read_config_data(path)
        
        cache_key = self.get_cache_key(path)
        user_cache_setting = self.get_option('cache')
        attempt_to_read_cache = user_cache_setting and cache
        cache_needs_update = user_cache_setting and not cache

        if attempt_to_read_cache:
            try:
                results = self._cache[cache_key]
            except KeyError:
                cache_needs_update = True
        
        if not attempt_to_read_cache or cache_needs_update:
            results = self._get_inventory_data()

        if cache_needs_update:
            self._cache[cache_key] = results

        self._populate_inventory(results)

    def _get_inventory_data(self):
        '''Fetch data from Incus'''
        remotes = self.get_option('remotes')
        projects = self.get_option('projects')
        tags_filter = self.get_option('tags')
        running_only = self.get_option('running_only')
        
        data = []

        for remote in remotes:
            for project in projects:
                cmd = ['incus', 'list', '--format=json', '--project', project, '{}:'.format(remote)]
                
                try:
                    output = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode('utf-8')
                    if not output.strip():
                        instances = []
                    else:
                        instances = json.loads(output)
                except subprocess.CalledProcessError as e:
                    raise AnsibleError("Failed to list instances for remote '{}' project '{}': {}".format(remote, project, e.stderr.decode('utf-8')))
                except Exception as e:
                     raise AnsibleError("Failed to parse incus output: {}".format(str(e)))

                for instance in instances:
                    if running_only and instance['status'] != 'Running':
                        continue

                    if tags_filter:
                        instance_config = instance.get('config', {})
                        match = True
                        for key, value in tags_filter.items():
                            config_key = 'user.' + key
                            if instance_config.get(config_key) != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    instance['inventory_remote'] = remote
                    instance['inventory_project'] = project
                    data.append(instance)
        
        return data

    def _populate_inventory(self, results):
        '''Populate Ansible inventory from fetched data'''
        
        for instance in results:
            name = instance['name']
            remote = instance['inventory_remote']
            project = instance['inventory_project']
            
            self.inventory.add_host(name)
            
            self.inventory.set_variable(name, 'ansible_connection', 'community.general.incus')
            self.inventory.set_variable(name, 'ansible_incus_remote', remote)
            self.inventory.set_variable(name, 'ansible_incus_project', project)
            self.inventory.set_variable(name, 'ansible_host', name)
            
            config = instance.get('config', {})
            tags = {}
            for key, value in config.items():
                var_name = 'incus_config_' + key.replace('.', '_').replace('-', '_')
                self.inventory.set_variable(name, var_name, value)
                
                if key.startswith('user.'):
                    tag_key = key[5:] 
                    tags[tag_key] = value
                    self.inventory.set_variable(name, 'tag_' + tag_key, value)

            self.inventory.set_variable(name, 'incus_user_tags', tags)

            remote_group = 'incus_remote_' + remote
            project_group = 'incus_project_' + project
            
            self.inventory.add_group(remote_group)
            self.inventory.add_child(remote_group, name)
            
            self.inventory.add_group(project_group)
            self.inventory.add_child(project_group, name)

            self._set_composite_vars(self.get_option('compose'), self.inventory.get_host(name).get_vars(), name, strict=True)
            self._add_host_to_composed_groups(self.get_option('groups'), self.inventory.get_host(name).get_vars(), name, strict=True)
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), self.inventory.get_host(name).get_vars(), name, strict=True)
