#!/usr/bin/python

# Put some comments here about what Hitachi Vantara's license is.
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: hnas_filesystem
short_description: This module creates/deletes/expands/mount/unmount Hitachi NAS filesystems
description:
  - The C(hnas_filesystem) module creates/deletes/expands/mount/unmount Hitachi NAS filesystems.
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
  state:
    description:
    - set state to C(present) to ensure the existance of a filesystem, and that it is at least the requested size
    - set state to C(absent) to ensure that specific filesystem is not present on the server
    type: str
    required: true
    choices: ['present', 'absent']
  data:
    description:
    - Additional data to describe the filesystem.
    - The label parameter is required for all operations, and is the only paramaeter required for the delete operation.
    - Either the storage_pool_name or storagePoolId parameter needs to be specified for all 'present' operations.
    - Either the virtual_server_name or virtualServerId parameter needs to be specified for all 'present' operations.
    - The capacity value is required for all 'present' operations.
    required: true
    type: dict
    suboptions:
      label:
        description: label or name of the filesystem
        type: str
        required: true
      storage_pool_name:
        description: name of the storage pool that should contain the filesystem
        type: str
      storagePoolId:
        description: ID of the storage pool that should contain the filesystem
        type: int
      virtual_server_name:
        description: name of the virtual server that should host the filesystem
        type: str
      virtualServerId:
        description: ID of the virtual server that should host the filesystem
        type: int
      capacity_unit:
        description: unit to use as a multiplier for the capacity value
        choices: ['b', 'bytes', 'k', 'kb', 'kib', 'm', 'mb', 'mib', 'g', 'gb', 'gib', 't', 'tb', 'tib']
        type: str
        default: bytes
      capacity:
        description:
        - Minimum capacity of the filesystem.
        - The capacity value will be dependant on the chunkSize of the storage pool.
        - The capacity value should be used in conjunction with the capacity_unit value.
        type: int
      status:
        description: required status of the filesystem
        choices: ['MOUNTED', 'NOT_MOUNTED']
        type: str
        default: MOUNTED
      blockSize:
        description: 
        - The filesystem block size to be used to format an unformatted/new filesystem.
        - Note that an existing filesystem will NOT be reformatted with a different block size.
        choices: [4, 32]
        type: int
        default: 4

'''

EXAMPLES = '''
- name: Create or Expand an HNAS filesystem
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hnas_filesystem:
      state: present
      <<: *login
      data:
        label: "ansible"
        virtualServerId: 1
        storage_pool_name: "Span0"
        capacity_unit: gib
        capacity: 20
    register: result
  - debug: var=result.filesystem


- name: Delete HNAS filesystem
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
    - hnas_filesystem:
        state: absent
        <<: *login
        data:
          label: "ansible"
      register: result
    - debug: var=result.filesystem


- name: Unmount an HNAS filesystem
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hnas_filesystem:
      state: present
      <<: *login
      data:
        label: "ansible"
        virtualServerId: 1
        storage_pool_name: "Span0"
        capacity_unit: gib
        capacity: 20
        status: "NOT_MOUNTED"
    register: result
  - debug: var=result.filesystem

'''

RETURN = '''
[root@localhost ~]# ansible-playbook hv_create_fs.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Create or expand an HNAS filesystem] **********************************************************************************************************************

TASK [hnas_filesystem] ******************************************************************************************************************************************
changed: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.filesystem": {
        "blockSize": 4096,
        "capacity": 19293798400,
        "expansionLimits": 18446744073709551615,
        "filesystemId": "075FA5699D6C5B4F0000000000000000",
        "freeCapacity": 16986300416,
        "isDedupeEnabled": false,
        "isDedupeSupported": false,
        "isLogicalCapacityFreeCapacityValid": true,
        "isLogicalCapacityValid": true,
        "isNDMPRecoveryTarget": false,
        "isNonStrictWORM": false,
        "isObjectReplicationTarget": false,
        "isReadCached": false,
        "isReadOnly": false,
        "isSysLocked": false,
        "isThinProvisioningEnabled": false,
        "isThinProvisioningEnabledValid": true,
        "isTrueSparseFileEnabled": true,
        "isTrueSparseFileEnabledValid": true,
        "isUnlimitedExpansion": true,
        "isWORM": false,
        "label": "ansible",
        "logicalCapacity": 19293798400,
        "logicalFreeCapacity": 16986300416,
        "objectId": "30373546413536393944364335423446303030303030303030303030303030303a3a3a303a3a3a4f49445f24232140255f56",
        "status": "MOUNTED",
        "storagePoolId": 530991019344831952,
        "usedCapacity": 2307497984,
        "virtualServerId": 1
    }
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0


[root@localhost ~]# ansible-playbook hv_delete_fs.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Delete HNAS filesystem] ***********************************************************************************************************************************

TASK [hnas_filesystem] ******************************************************************************************************************************************
changed: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.filesystem": ""
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0


[root@localhost ~]# ansible-playbook hv_unmount_fs.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Unmount an HNAS filesystem] *******************************************************************************************************************************

TASK [hnas_filesystem] ******************************************************************************************************************************************
changed: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.filesystem": {
        "blockSize": 4096,
        "capacity": 19293798400,
        "expansionLimits": 18446744073709551615,
        "filesystemId": "075FA51B34E538F70000000000000000",
        "freeCapacity": 16986927104,
        "isDedupeEnabled": false,
        "isDedupeSupported": false,
        "isLogicalCapacityFreeCapacityValid": false,
        "isLogicalCapacityValid": false,
        "isNDMPRecoveryTarget": false,
        "isNonStrictWORM": false,
        "isObjectReplicationTarget": false,
        "isReadCached": false,
        "isReadOnly": false,
        "isSysLocked": false,
        "isThinProvisioningEnabled": false,
        "isThinProvisioningEnabledValid": true,
        "isTrueSparseFileEnabled": false,
        "isTrueSparseFileEnabledValid": false,
        "isUnlimitedExpansion": true,
        "isWORM": false,
        "label": "ansible",
        "logicalCapacity": 0,
        "logicalFreeCapacity": 0,
        "objectId": "30373546413531423334453533384637303030303030303030303030303030303a3a3a303a3a3a4f49445f24232140255f56",
        "status": "NOT_MOUNTED",
        "storagePoolId": 530991019344831952,
        "usedCapacity": 2306871296,
        "virtualServerId": 1
    }
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

'''

import json

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, get_exception

import ansible.module_utils.hv_hnas_main as server


def main():
    argument_spec = basic_auth_argument_spec()
    argument_spec.update(
        api_key = dict(type='str', required=False, no_log=True),
        state=dict(type='str', choices=['present','absent'], default='present'),
        data=dict(type='dict', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
# direct params cover authentication and operation
    params = module.params
# variables are specific to the operation being carried out
    variables = params['data']

    api_url = params['api_url']
    api_key = params.get('api_key', None)
    api_username = params.get('api_username', None)
    api_password = params.get('api_password', None)
    validate_certs = params['validate_certs']
    filesystem = ""
    try:
        assert 'label' in variables, "Missing 'label' data value"
        state = params['state']
        hnas = server.HNASFileServer(api_url, verify=validate_certs)
        hnas.set_credentials(api_key, api_username, api_password)
        if state == "absent":
            changed = hnas.delete_filesystem(label=variables['label'])
        elif state == "present":
            if 'virtual_server_name' not in variables:
                assert 'virtualServerId' in variables, "Missing 'virtualServerId' or 'virtual_server_name' data value"
            if 'storage_pool_name' not in variables:
                assert 'storagePoolId' in variables, "Missing 'storagePoolId' or 'storage_pool_name' data value"
            assert 'capacity' in variables, "Missing 'capacity' data value"
            changed, success, filesystem = hnas.create_filesystem(variables)
            assert success == True, "An existing filesystem exists, with the same name, but the parameters do not match"

    except:
        error = get_exception()
        module.fail_json(msg="HNAS filesystem task failed on system at [%s] due to [%s]" % (api_url, str(error)))

    result = dict(changed=changed, filesystem=filesystem)
    module.exit_json(msg="HNAS filesystem task completed successfully on system at [%s]" % (hnas.get_address()), **result)

if __name__ == '__main__':
    main()
