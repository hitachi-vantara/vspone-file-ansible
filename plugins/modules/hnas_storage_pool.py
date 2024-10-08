#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021-2024, Hitachi Vantara, LTD


DOCUMENTATION = r'''
---
module: hnas_storage_pool
short_description: This module manages Hitachi NAS storage pools
description:
  - This module allows the creation and deletion of Hitachi NAS storage pools.
  - The presence of a storage pool allows filesystems to be created.
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
    - If I(state=present), ensure the existence of a storage pool.
    - If I(state=absent), ensure that specific storage pool is not present on the server.
    type: str
    required: true
    choices: ['present', 'absent']
  data:
    description:
    - Additional data to describe the storage pool.
    - The I(label) parameter is required for both create and delete operations.
    - The other parameters are only required for the create operation.
    required: true
    type: dict
    suboptions:
      label:
        description: label or name of the storage pool
        type: str
        required: true
      chunkSize:
        description: 
        - The chunk size determines the ultimate scalability of the storage pool and its filesystems.
        - It also controls the size of the increments in which space can be added to filesystems.
        - The chunksize cannot be changed once a storage pool has been created.
        type: int
        default: 19327352832
      systemDrives:
        description:
        - A list of system drive ID values
        - Minimum number of system drives to create a storage pool is 4, and the maximum is 16
        type: list
        required: true
      allow_denied_system_drives:
        description: Allows the use of system drives that currently are denied access
        type: boolean
        default: false

'''

EXAMPLES = r'''
- name: Create Hitachi NAS storage pool
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hitachivantara.hnas.hnas_storage_pool:
      state: present
      <<: *login
      data:
        label: "ansible-pool"
        systemDrives: [ 16, 17, 18, 19, 20, 21 ]
    register: result
  - debug: var=result.storagePool


- name: Delete Hitachi NAS storage pool
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
    - hitachivantara.hnas.hnas_storage_pool:
        state: absent
        <<: *login
        data:
          label: "ansible-pool"
      register: result
    - debug: var=result.storagePool

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
    pool = ""
    try:
        assert 'label' in variables, "Missing 'label' data value"
        state = params['state']
        hnas = server.HNASFileServer(api_url, verify=validate_certs)
        hnas.set_credentials(api_key, api_username, api_password)
        if state == "absent":
            changed = hnas.delete_storage_pool(label=variables['label'])
        elif state == "present":
            changed, success, pool = hnas.create_storage_pool(variables)
            assert success == True, "An existing storage pool exists, with the same name, but the parameters do not match"

    except:
        error = get_exception()
        module.fail_json(msg="Hitachi NAS storage pool task failed on system at [%s] due of [%s]" % (api_url, str(error)))

    result = dict(changed=changed, storagePool=pool)
    module.exit_json(msg="Hitachi NAS storage pool task completed successfully on system at [%s]" % (hnas.get_address()), **result)

if __name__ == '__main__':
    main()
