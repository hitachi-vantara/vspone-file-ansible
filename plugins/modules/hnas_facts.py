#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021-2024, Hitachi Vantara, LTD


DOCUMENTATION = r'''
---
module: hnas_facts
short_description: This module gathers various facts about Hitachi NAS servers
description:
  - This module gathers various facts about Hitachi NAS server.
  - It can gather storage details and also file serving details.
version_added: "1.0.0"
author: Hitachi Vantara, LTD.
options:
  api_key:
    description: The REST API authentication key - the preferred authentication method.
    type: str
  api_username:
    description: The username to authenticate with the REST API.
    type: str
  api_password:
    description: The password to authenticate with the REST API.
    type: str
  api_url:
    description:
    - The URL to access the Hitachi NAS REST API.  This needs to include the protocol, address, port and API version.
    type: str
    required: true
    example:
    - https://10.1.2.3:8444/v7
  validate_certs:
    description: Should https certificates be validated?
    type: bool
    default: true
  fact_type:
    description:
    - A list of required facts.  Valid list items are
    -  C(system_facts)         - gather details about the Hitachi NAS cluster, including node information
    -  C(virtual_server_facts) - gather details about the virtual servers hosted on the cluster
    -  C(system_drive_facts)   - gather details about the system drives visible to the cluster
    -  C(storage_pool_facts)   - gather details about the storage pools hosted on the cluster
    -  C(filesystem_facts)     - gather details about the filesystems hosted on the cluster
    -  C(nfs_export_facts)     - gather details of NFS exports hosted on a particular virtual server
    -  C(cifs_share_facts)     - gather details of SMB/CIFS shares hosts on a particular virtual server
    -  C(snapshot_facts)       - gather a list of snapshots present on s particular filesystem
    -  C(network_port_facts)   - gather a list of the physical network ports available to each cluster node
    -  C(aggregate_port_facts) - gather a list of the aggregate network ports available to each cluster node
    -  C(virtual_volume_facts) - gather details about virtual volumes and any associated quota, on a particular filesystem
    choices:
      system_facts:
        description: gather details about the Hitachi NAS cluster, including node information
      virtual_server_facts:
        description: gather details about the virtual servers hosted on the cluster
      system_drive_facts:
        description: gather details about the system drives visible to the cluster
      storage_pool_facts:
        description: gather details about the storage pools hosted on the cluster
      filesystem_facts:
        description: gather details about the filesystems hosted on the cluster
      nfs_export_facts:
        description: gather details of NFS exports hosted on a particular virtual server
      cifs_share_facts:
        description: gather details of SMB/CIFS shares hosts on a particular virtual server
      snapshot_facts:
        description: gather a list of snapshots present on s particular filesystem
      network_port_facts:
        description: gather a list of the physical network ports available to each cluster node
      aggregate_port_facts:
        description: gather a list of the aggregate network ports available to each cluster node
      virtual_volume_facts:
        description: gather details about virtual volumes and any associated quota, on a particular filesystem

    type: list
    elements: str
    required: true
  data:
    description:
    - Provides additional data when facts to be gathered are associated with a specific resource
    type: dict
    suboptions:
      filesystemId:
        description: C(filesystemId) parameter specifying a filesystem - required when retrieving I(snapshot_facts), otherwise not required
        type: str
      virtualServerId:
        description: C(virtualServerId) parameter specifying a virtual server - required when retrieving I(nfs_export_facts) or I(smb_share_facts), otherwise not required
        type: int

'''

EXAMPLES = r'''
- name: Get Hitachi NAS network aggregate ports
  hosts: localhost
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hitachi.hnas.hnas_facts: 
      <<: *login
      fact_type:
        - aggregate_port_facts
    register: result
  - debug: var=result.ansible_facts


- name: Get Hitachi NAS system information
  hosts: localhost
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hitachi.hnas.hnas_facts: 
      <<: *login
      fact_type:
        - system_facts
    register: result
  - debug: var=result.ansible_facts


- name: Get NFS Export details for virtual server 1
  hosts: localhost
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hitachi.hnas.hnas_facts: 
      <<: *login
      fact_type:
        - nfs_export_facts
      data:
        virtualServerId: 1
    register: result
  - debug: var=result.ansible_facts

'''

RETURN = r'''

'''

import json

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, get_exception

import ansible_collections.hitachi.hnas.plugins.module_utils.hnas_main as server


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
            facts['storagePools'] = hnas.get_storage_pools(label=label)['storagePools']
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
        if 'virtual_volume_facts' in fact_type:
            assert virtualServerId != None, "Missing 'virtualServerId' data value"
            assert filesystemId != None, "Missing 'filesystemId' data value"
            facts['virtualVolumes'] = hnas.get_virtual_volumes(virtualServerId=virtualServerId, filesystemId=filesystemId, name=name)['virtualVolumes']

    except:
        error = get_exception()
        module.fail_json(msg="Failed to obtain facts from system at [%s] because of [%s]" % (api_url, str(error)))

    result = dict(ansible_facts=facts, changed=False)
    module.exit_json(msg="Gathered facts from system at [%s]" % (hnas.get_address()), **result)


if __name__ == '__main__':
    main()
