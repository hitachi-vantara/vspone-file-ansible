#!/usr/bin/python

# Put some comments here about what Hitachi Vantara's license is.
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: hnas_get_system_facts

short_description: This is my test module

version_added: "0.1"

short_description: Get facts about a Hitachi NAS Cluster

options:
  api_key:
    required: false
    description:
    - The REST API application key.
  api_username:
    required: false
    description:
    - The username to authenticate with the REST API.
  api_password:
    required: false
    description:
    - The password to authenticate with the REST API.
  admin_vnode_address:
    required: true
    description:
    - The the name or IP address of the admin vnode to access the REST API.
    example:
    - nas1.mycompany.com
    - 10.0.0.1
  validate_certs:
    required: false
    default: true
    description:
    - Should https certificates be validated?

description:
    - Return various information about a Hitachi NAS cluster (eg, configuration, volumes, file systems)


author:
    - Phil Cobley 
'''

EXAMPLES = '''
    - name: Get cluster facts using api key
      hnas_facts:
        admin_vnode_address: "{{ hnas_admin__vnode_address }}"
        api_key: "{{ hnas_api_key }}"
        validate_certs: "{{ validate_certs }}"

    - name: Get cluster facts using username and password
      hnas_facts:
        admin_vnode_address: "{{ hnas_admin__vnode_address }}"
        api_username: "{{ netapp_api_username }}"
        api_password: "{{ netapp_api_password }}"
        validate_certs: "{{ validate_certs }}"

'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: Gathered facts for <NASClusterID>.
    type: str
    returned: always
'''

import json

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, get_exception

import ansible.module_utils.hnas_main as server


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(
        api_key=dict(type='str', required=False, no_log=True),
        fact_type=dict(type='list', elements='str'),
        data=dict(type='dict', required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    params = module.params
    api_url = params['api_url']
    api_key = params.get('api_key', None)
    api_username = params.get('api_username', None)
    api_password = params.get('api_password', None)
    validate_certs = params['validate_certs']
    fact_type = params['fact_type']

    if fact_type is None:
        fact_type = ['system_facts']

    label = None
    virtualServerId = None
    name = None
    filesystemId = None
    if 'data' in params and params['data'] != None:
        variables = params['data']
        label = variables.get('label', None)
        name = variables.get('name', None)
        virtualServerId = variables.get('virtualServerId', None)
        filesystemId = variables.get('filesystemId', None)

    facts = {}
    try:
        hnas = server.HNASFileServer(api_url, verify=validate_certs)
        hnas.set_credentials(api_key, api_username, api_password)
        if 'system_facts' in fact_type:
            facts['system'] = hnas.get_file_server_info()
            facts['nodes'] = hnas.get_nodes()['nodes']
        if 'virtual_server_facts' in fact_type:
            facts['virtualServers'] = hnas.get_virtual_servers(virtualServerId=virtualServerId, name=name)['virtualServers']
        if 'system_drive_facts' in fact_type:
            facts['systemDrives'] = hnas.get_system_drives()['systemDrives']
        if 'storage_pool_facts' in fact_type:
            facts['storagePools'] = hnas.get_storage_pools()['storagePools']
        if 'filesystem_facts' in fact_type:
            facts['filesystems'] = hnas.get_file_systems(virtualServerId=virtualServerId, label=label)['filesystems']
        if 'nfs_export_facts' in fact_type:
            assert virtualServerId != None, "Missing 'virtualServerId' data value"
            facts['nfsExports'] = hnas.get_exports(virtualServerId, name=name)['filesystemShares']
        if 'cifs_share_facts' in fact_type:
            assert virtualServerId != None, "Missing 'virtualServerId' data value"
            facts['cifsShares'] = hnas.get_shares(virtualServerId, name=name)['filesystemShares']
        if 'snapshot_facts' in fact_type:
            assert filesystemId != None, "Missing 'filesystemId' data value"
            facts['snapshots'] = hnas.get_snapshots(filesystemId)['snapshots']
        if 'network_port_facts' in fact_type:
            facts['networkPorts'] = hnas.get_network_interfaces(physical=True)['ports']
        if 'aggregate_port_facts' in fact_type:
            facts['aggregatePorts'] = hnas.get_network_interfaces(physical=False)['ports']

    except:
        error = get_exception()
        module.fail_json(msg="Failed to obtain facts from system at [%s] because of [%s]" % (api_url, str(error)))

    result = dict(ansible_facts=facts, changed=False)
    module.exit_json(msg="Gathered facts from system at [%s]" % (hnas.get_address()), **result)


if __name__ == '__main__':
    main()
