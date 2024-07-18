#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021-2024, Hitachi Vantara, LTD


DOCUMENTATION = r'''
---
module: hnas_filesystem
short_description: This module creates/deletes/expands/mount/unmount Hitachi NAS filesystems
description:
  - This module can be used to create or delete filesystems on Hitachi NAS servers.
  - It can also be used to expand an existing filesystem, by increasing the capacity.
  - The state of filesystem can be set to mounted or unmounted by setting the I(status) appropriately.
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
  state:
    description:
    - If I(state=present), ensure the existence of a filesystem, with the requested I(status), and that it is at least the requested I(capacity).
    - If I(state=absent), ensure that specific filesystem is not present on the server.
    type: str
    required: true
    choices: ['present', 'absent']
  data:
    description:
    - Additional data to describe the filesystem.
    - The I(label) parameter is required for all operations, and is the only parameter required for the delete operation.
    - Either the I(storage_pool_name) or I(storagePoolId) parameter needs to be specified for all C(present) operations.
    - Either the I(virtual_server_name) or I(virtualServerId) parameter needs to be specified for all C(present) operations.
    - The I(capacity) value is required for all C(present) operations.
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
        description: unit to use as a multiplier for the I(capacity) value
        choices: ['b', 'bytes', 'k', 'kb', 'kib', 'm', 'mb', 'mib', 'g', 'gb', 'gib', 't', 'tb', 'tib']
        type: str
        default: bytes
      capacity:
        description:
        - Minimum capacity of the filesystem.
        - The I(capacity) value will be dependent on the chunkSize of the storage pool.  See M(hnas_storage_pool).
        - The I(capacity) value should be used in conjunction with the I(capacity_unit) value.
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

EXAMPLES = r'''
- name: Create or Expand an Hitachi NAS filesystem
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hitachivantara.hnas.hnas_filesystem:
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


- name: Delete Hitachi NAS filesystem
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
    - hitachivantara.hnas.hnas_filesystem:
        state: absent
        <<: *login
        data:
          label: "ansible"
      register: result
    - debug: var=result.filesystem


- name: Unmount an Hitachi NAS filesystem
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hitachivantara.hnas.hnas_filesystem:
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

RETURN = r'''

'''

import json

from ansible.module_utils.api import basic_auth_argument_spec
from ansible.module_utils.basic import AnsibleModule, get_exception

import ansible_collections.hitachivantara.hnas.plugins.module_utils.hnas_main as server


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
        module.fail_json(msg="Hitachi NAS filesystem task failed on system at [%s] due to [%s]" % (api_url, str(error)))

    result = dict(changed=changed, filesystem=filesystem)
    module.exit_json(msg="Hitachi NAS filesystem task completed successfully on system at [%s]" % (hnas.get_address()), **result)

if __name__ == '__main__':
    main()
