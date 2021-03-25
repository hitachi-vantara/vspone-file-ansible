#!/usr/bin/python

# Put some comments here about what Hitachi Vantara's license is.
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: hv_hnas_facts
short_description: This module gathers various facts about Hitachi NAS virtual servers
description:
  - The hv_hnas_facts module gathers various facts about Hitachi NAS virtual servers.
version_added: "0.1"
author:
  - Hitachi Vantara, LTD.
requirements:
options:
  api_key:
    description:
    - The REST API authentication key - the preferred authentication method.
    type: str
    required: false
  api_username:
    description:
    - The username to authenticate with the REST API.
    type: str
    required: false
  api_password:
    description:
    - The password to authenticate with the REST API.
    type: str
    required: false
  api_url:
    description:
    - The URL to access the Hitachi NAS REST API.  This needs to include the protocol, address, port and API version.
    type: str
    required: true
    example:
    - https://10.1.2.3:8444/v7
  validate_certs:
    description:
    - Should https certificates be validated?
    type: bool
    required: false
    default: true
  fact_type:
    description:
    - A list of required facts.  Valid list items are:
    - system_facts         - gather details about the HNAS cluster, including node information
    - virtual_server_facts - gather details about the virtual servers hosted on the cluster
    - system_drive_facts   - gather details about the system drives visible to the cluster
    - storage_pool_facts   - gather details about the storage pools hosted on the cluster
    - filesystem_facts     - gather details about the filesystems hosted on the cluster
    - nfs_export_facts     - gather details of NFS exports hosted on a particular virtual server
    - cifs_share_facts     - gather details of SMB/CIFS shares hosts on a particular virtual server
    - snapshot_facts       - gather a list of snapshots present on s particular filesystem
    - network_port_facts   - gather a list of the physical network ports available to each cluster node
    - aggregate_port_facts - gather a list of the aggregate network ports available to each cluster node
    type: list
    required: true
  data:
    description:
    - Provides additional data when facts to be gathered are associated with a specific resource
    required: false
    type: dict
    suboptions:
      filesystemId:
        description: filesystemId of a filesystem - required when retrieving snapshot_facts, otherwise not required
        type: str
      virtualServerId:
        description: virtualServerId parameter of a virtual server - required when retrieving nfs_export_facts or smb_share_facts, otherwise not required
        type: int
'''

EXAMPLES = '''
- name: Get Hitachi NAS network aggregate ports
  hosts: localhost
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hv_hnas_facts: 
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
  - hv_hnas_facts: 
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
  - hv_hnas_facts: 
      <<: *login
      fact_type:
        - nfs_export_facts
      data:
        virtualServerId: 1
    register: result
  - debug: var=result.ansible_facts

'''

RETURN = '''
[root@localhost ~]# ansible-playbook hv_get_aggregate_facts.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Get Hitachi NAS network aggregate ports] ******************************************************************************************************************

TASK [Gathering Facts] ******************************************************************************************************************************************
ok: [localhost]

TASK [hv_hnas_facts] ********************************************************************************************************************************************
ok: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.ansible_facts": {
        "aggregatePorts": [
            "ag1",
            "ag1-vlan0099",
            "ag2"
        ]
    }
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0


[root@localhost ~]# ansible-playbook hv_get_system_facts.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Get Hitachi NAS system information] ***********************************************************************************************************************

TASK [Gathering Facts] ******************************************************************************************************************************************
ok: [localhost]

TASK [hv_hnas_facts] ********************************************************************************************************************************************
ok: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.ansible_facts": {
        "nodes": [
            {
                "UUID": "48fbe624-4c33-11d0-9001-9c5547075e75",
                "firmwareVersion": "13.9.6813.00",
                "ipAddresses": [
                    "172.27.5.10"
                ],
                "model": "3090-G2",
                "name": "mercury110n1-1",
                "nodeId": 1,
                "objectId": "313a3a3a3a3a3a303a3a3a4f49445f24232140255f56",
                "serial": "M2SEKW1238092",
                "status": "ONLINE"
            }
        ],
        "system": {
            "clusterUUID": "48fbe624-4c33-11d0-9000-9c5547075e75",
            "firmwareVersion": "13.9.6813.00",
            "isCluster": false,
            "licenses": [
                "CIFS",
                "NFS",
                "FILE_CLONE",
                "BASE_DEDUPLICATION",
            ],
            "model": "3090-G2",
            "name": "mercury110n1",
            "nodeCount": 1,
            "storageHealth": "ROBUST",
            "vendor": "HITACHI"
        }
    }
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0


[root@localhost ~]# ansible-playbook hv_get_nfs_export_facts.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Get NFS Export details for virtual server 1] **************************************************************************************************************

TASK [Gathering Facts] ******************************************************************************************************************************************
ok: [localhost]

TASK [hv_hnas_facts] ********************************************************************************************************************************************
ok: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.ansible_facts": {
        "nfsExports": [
            {
                "filesystemId": "075E4D861BBF9C360000000000000000",
                "name": "/nfse",
                "objectId": "313a3a3a36333463396164632d306332312d313164372d396437642d3963353534373037356537353a3a3a303a3a3a4f49445f24232140255f56",
                "path": "/",
                "settings": {
                    "accessConfig": "*(rw)",
                    "localReadCacheOption": "DISABLED",
                    "snapshotOption": "SHOW_AND_ALLOW_ACCESS",
                    "transferToReplicationTargetSetting": "USE_FS_DEFAULT"
                },
                "shareId": "634c9adc-0c21-11d7-9d7d-9c5547075e75",
                "virtualServerId": 1
            }
        ]
    }
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

'''

import json

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, get_exception

import ansible.module_utils.hv_hnas_main as server


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
