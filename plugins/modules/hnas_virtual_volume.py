#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021-2024, Hitachi Vantara, LTD


DOCUMENTATION = r'''
---
module: hnas_virtual_volume
short_description: This module manages Hitachi NAS virtual volumes
description:
  - This module allows the creation and deletion of Hitachi NAS virtual volumes.
  - It also allows the virtual volumes quota to be created and updated.
version_added: "1.1.0"
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
    - If I(state=present), ensure the existence of a virtual volume and its quota.
    - If I(state=absent), ensure that a specific virtual volume is not present on the server.
    type: str
    required: true
    choices: ['present', 'absent']
  data:
    description:
    - Additional data to describe the virtual volume and its quota.
    - The I(name), I(virtualServerId) and I(filesystemId) parameters are required for all operations.
    - The I(quota) parameter can be used to add or update the virtual volumes quota.
    - The I(remove_content) parameter is only relevant for I(state=absent).
    required: true
    type: dict
    suboptions:
      name:
        description: Name of the virtual volume
        type: str
        required: true
      virtualServerId:
        description: C(virtualServerId) parameter of the virtual server that hosts the virtual volume
        type: int
        required: true
      filesystemId:
        description: C(filesystemId) of the filesystem which will host the virtual volume.
        type: str
        required: true
      filesystemPath:
        description: 
        - filesystem location that is the root of the virtual volume
        - The path should be in UNIX format - '/folder/sub-folder'
        type: str
      emails:
        description: List of email address contacts for the virtual volume.
        type: list
        elements: str
      remove_content:
        description:
        - A non-empty virtual volume can not be removed from an HNAS system.
        - This option will removes a virtual volume and its contents.
        - This option allows the removal of user data, and should be used with caution.
        type: bool
        default: false
      quota:
        description: Details about the quota associated with the virtual volume.
        type: dict
        suboptions:
          logEvent:
            description: Whether to add quota's events to the event log.
            type: bool
            default: false
          diskUsageThreshold:
            description: The amount of disk space that the quota is able to consume.
            type: dict
            suboptions:
              isHard:
                description: Whether the limit value is a hard limit, or allowed to be exceeded.
                type: bool
                default: true
              limit:
                description: The maximum allowed limit for the quota item type.
                type: int
                default: 0
              severe:
                description: Severe threshold for logging an event for the quota item type, as a percentage.
                type: int
                default: 0
              warning:
                description: Warning threshold for logging an event for the quota item type, as a percentage.
                type: int
                default: 0
              reset:
                description: Amount by which usage must fall below a threshold before re-logging its event, as a percentage.
                type: int
                default: 5
          fileCountThreshold:
            description: The number of files that are allowed by the quota.
            type: dict
            suboptions:
              isHard:
                description: Whether the limit value is a hard limit, or allowed to be exceeded.
                type: bool
                default: true
              limit:
                description: The maximum allowed limit for the quota item type.
                type: int
                default: 0
              severe:
                description: Severe threshold for logging an event for the quota item type, as a percentage.
                type: int
                default: 0
              warning:
                description: Warning threshold for logging an event for the quota item type, as a percentage.
                type: int
                default: 0
              reset:
                description: Amount by which usage must fall below a threshold before re-logging its event, as a percentage.
                type: int
                default: 5

'''

EXAMPLES = r'''

- name: Create or update an Hitachi NAS virtual volume, and its associated quota
  hosts: localhost
  gather_facts: false
  collections:
  - hitachi.hnas
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hnas_virtual_volume:
      state: present
      <<: *login
      data:
        name: "ansible-vv"
        virtualServerId: 1
        filesystemId: "075E75D0D373CA7D0000000000000000"
        filesystemPath: "/ansible-vv"
        emails: 
        - bob@example.com
        - dave@example.com
        quota:
          logEvent: true
          diskUsageThreshold:
            isHard: false
            limit: 12345678
            reset: 5
            severe: 90
            warning: 70
          fileCountThreshold:
            isHard: false
            limit: 700
            reset: 5
            severe: 85
            warning: 70
    register: result
  - debug: var=result.virtualVolume


- name: Delete an Hitachi NAS virtual volume, and ensure the contents are also removed
  hosts: localhost
  gather_facts: false
  collections:
  - hitachi.hnas
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hnas_virtual_volume:
      state: absent
      <<: *login
      data:
        name: "ansible-vv"
        virtualServerId: 1
        filesystemId: "075E75D0D373CA7D0000000000000000"
        remove_content: true
    register: result
  - debug: var=result.virtualVolume

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
    virtual_volume = ""
    try:
        state = params['state']
        hnas = server.HNASFileServer(api_url, verify=validate_certs)
        hnas.set_credentials(api_key, api_username, api_password)
        if state == "absent":
            changed = hnas.delete_virtual_volume(variables)
        elif state == "present":
            changed, success, virtual_volume = hnas.create_virtual_volume(variables)
            assert success == True, "The requested virtual volume operation failed"

    except:
        error = get_exception()
        module.fail_json(msg="Hitachi NAS virtual volume task failed on system at [%s] due of [%s]" % (api_url, str(error)))

    result = dict(changed=changed, virtualVolume=virtual_volume)
    module.exit_json(msg="Hitachi NAS virtual volume task completed successfully on system at [%s]" % (hnas.get_address()), **result)

if __name__ == '__main__':
    main()
