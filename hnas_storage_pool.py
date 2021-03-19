#!/usr/bin/python

# Put some comments here about what Hitachi Vantara's license is.
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: hnas_get_filesystem_facts

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
        module.fail_json(msg="HNAS storage pool task failed on system at [%s] due of [%s]" % (api_url, str(error)))

    result = dict(changed=changed, storagePool=pool)
    module.exit_json(msg="HNAS storage pool task completed successfully on system at [%s]" % (hnas.get_address()), **result)

if __name__ == '__main__':
    main()
