#!/usr/bin/python
# -*- coding: utf-8 -*-

# Put some comments here about what Hitachi Vantara's license is.
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: hnas_virtual_server
short_description: This module creates/deletes Hitachi NAS virtual servers, and adds/deletes IP addresses
description:
  - This module can be used to ensure that a virtual server does or does not exist on a Hitachi NAS server.
  - IP addresses can also be added or removed from virtual servers.
version_added: "0.1"
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
    - If I(state=present), ensure the existence of a virtual server, or ensure that IP addresses are assigned to a virtual server.
    - If I(state=absent), ensure that specific IP addresses are not assigned to a virtual server, or that a virtual server is not present.
    type: str
    required: true
    choices: ['present', 'absent']
  data:
    description:
    - Additional data to describe the virtual server.
    - The I(name) parameter is required for both create and delete operations.
    - The I(address_details) parameter can be used to add and remove multiple addresses from virtual servers
    - The other parameters are only required for the create operation.
    required: true
    type: dict
    suboptions:
      name:
        description: Name of the virtual server
        type: str
        required: true
      clusterNodeId:
        description: Node that initially hosts the virtual server
        type: int
        default: 1
      address_details:
        description:
        - A list of IP addresses that should be present/absent from a virtual server.
        - If I(state=present), I(netmask) and I(port) need to be supplied for each address
        - If I(state=absent), just the I(address) parameter is needed
        - If the I(address_details) parameter is not present and I(state=absent), then the virtual server is deleted
        type: dict
        suboptions:
          address:
            description: IP address to associated with/removed from the virtual server
            type: str
          netmask:
            description: Network mask associated with the address parameter
            type: str
          port:
            description: Aggregate network port for address association
            type: str

'''

EXAMPLES = r'''

- name: Create Hitachi NAS virtual server
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
  tasks:
  - hitachi.hnas.hnas_virtual_server:
      <<: *login
      state: present
      data:
        name: "evs-ansible"
        address_details:
        - address: "172.27.5.15"
          netmask: "255.255.192.0"
          port: "ag1"
        - address: "172.27.5.16"
          netmask: "255.255.192.0"
          port: "ag1"
    register: result
  - debug: var=result.virtualServer


- name: Delete Hitachi NAS virtual server
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
  tasks:
  - hitachi.hnas.hnas_virtual_server:
      <<: *login
      state: absent
      data:
        name: "evs-ansible"
    register: result
  - debug: var=result.virtualServer


- name: Delete IP address from Hitachi NAS virtual server
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
  tasks:
  - hitachi.hnas.hnas_virtual_server:
      <<: *login
      state: absent
      data:
        name: "evs-ansible"
        address_details:
        - address: "172.27.5.15"
    register: result
  - debug: var=result.virtualServer

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
    virtual_server = ""
    try:
        assert 'name' in variables, "Missing 'name' data value"
        state = params['state']
        hnas = server.HNASFileServer(api_url, verify=validate_certs)
        hnas.set_credentials(api_key, api_username, api_password)
        if state == "absent":
            changed, success, virtual_server = hnas.delete_virtual_server(name=variables['name'], params=variables)
        elif state == "present":
            changed, success, virtual_server = hnas.create_virtual_server(variables)
        assert success == True, "The requested virtual server operation failed"

    except:
        error = get_exception()
        module.fail_json(msg="HNAS virtual server task failed on system at [%s] due of [%s]" % (api_url, str(error)))

    result = dict(changed=changed, virtualServer=virtual_server)
    module.exit_json(msg="HNAS virtual server task completed successfully on system at [%s]" % (hnas.get_address()), **result)

if __name__ == '__main__':
    main()
