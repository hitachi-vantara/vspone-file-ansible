#!/usr/bin/python
# -*- coding: utf-8 -*-

# Put some comments here about what Hitachi Vantara's license is.
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: hv_hnas_share_export
short_description: This module manages CIFS/SMB shares and NFS exports on Hitachi NAS servers
description:
  - This module creates and deletes CIFS/SMB shares and NFS exports on Hitachi NAS servers.
  - It is also possible to update existing shares and exports by changing the supplied parameters.
  - For CIFS/SMB shares, share access authentications can also be updated.
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
    - If I(state=present), ensure the existence of a share/export, and that it is in the requested state/configuration.
    - If I(state=absent), ensure that specific share/export is not present on the server.
    - should mention SAA
    type: str
    required: true
    choices: ['present', 'absent']
  data:
    description:
    - Additional data to describe the CIFS/SMB share or NFS export.
    - The I(name), I(virtualServerId) and I(type) parameters are required for all operations
    - The other parameters are only required for I(present) operations
    - Some parameters are applicable to NFS exports only
    - Some parameters are applicable to CIFS/SMB shares only
    - Some parameters are applicable to both NFS exports and CIFS/SMB shares.
    required: true
    type: dict
    suboptions:
      name:
        description: name of the share/export
        type: str
        required: true
      virtualServerId:
        description: C(virtualServerId) parameter of the virtual server that hosts the share/export
        type: int
        required: true
      filesystemId:
        description: C(filesystemId) of the filesystem associated with the share/export
        type: str
      filesystemPath:
        description: 
        - filesystem location that is exported by the share/export
        - If I(type=nfs) the path should be in UNIX format - '/folder/sub-folder'
        - If I(type=cifs) the path should be in Windows format - '\\\\folder\\\\sub-folder'
        type: str
      type:
        description: If I(type=nfs) refers to an NFS export, and I(type=cifs) refers to a CIFS/SMB share
        type: str
        choices: ["nfs", "cifs"]
        required: true
      accessConfig:
        description: Set the client access restrictions for this share/export.  By default all clients have read and write access.
        type: str
      snapshotOption:
        description: Sets the accessibility and visibility of the snapshot directory.
        type: str
        choices: ["HIDE_AND_DISABLE_ACCESS", "HIDE_AND_ALLOW_ACCESS", "SHOW_AND_ALLOW_ACCESS"]
        default: "SHOW_AND_ALLOW_ACCESS"
      transferToReplicationTargetSetting:
        description: Sets whether the share or export should be brought online when the replication target of this shares/exports file system is converted to read-write.
        type: str
        choices: ["DO_NOT_TRANSFER", "TRANSFER", "USE_FS_DEFAULT", "INVALID"]
        default: "USE_FS_DEFAULT"
      localReadCacheOption:
        description: Sets which files are candidates for read caching.  Valid if I(type=nfs).
        type: str
        choice: ["DISABLED", "ENABLED_FOR_ALL_FILES", "ENABLED_FOR_TAGGED_FILES", "ENABLED_FOR_CVLS"]
        default: "DISABLED"
      comment:
        description: A comment associated with the share.  Valid if I(type=cifs).
        type: str
      userHomeDirectoryPath:
        description: Per-user home directories will be created using this path, relative to the share root.  Valid if I(type=cifs).
        type: str
      isScanForVirusesEnabled:
        description: If virus scanning is enabled, scan files accessed via this share for viruses.  Valid if I(type=cifs).
        type: bool
        default: false
      maxConcurrentUsers:
        description: Controls the maximum allowed connections.  -1 allows unlimited client connections.  Valid if I(type=cifs).
        type: int
        default: -1
      cacheOption:
        description: Specifies the share's cache options.  Valid if I(type=cifs).
        type: str
        choice: ["MANUAL_CACHING_DOCS", "AUTO_CACHING_DOCS", "AUTO_CACHING_PROGS", "CACHING_OFF"]
        default: "MANUAL_CACHING_DOCS"
      userHomeDirectoryMode:
        description: Set the share's home directory behavior.  Valid if I(type=cifs).
        type: str
        choice: ["OFF", "ADS", "USER", "HIDDEN_USER", "DOMAIN_AND_USER", "UNIX"]
        default: "OFF"
      isFollowSymbolicLinks:
        description: 
        - If symlinks are encountered when browsing this share, follow them automatically on the server. 
        - If client side symlink handling is enabled, this setting does not affect clients using the SMB2 or SMB3 protocols.
        - Valid if I(type=cifs).
        type: bool
        default: false
      isFollowGlobalSymbolicLinks:
        description: Allow clients that are connected to this share to follow global symlinks.  Valid if I(type=cifs).
        type: bool
        default: false
      isForceFileNameToLowercase:
        description: Convert the names of all files and directories created to lower case.  Valid if I(type=cifs).
        type: bool
        default: false
      isABEEnabled:
        description: Enable Access-based Enumeration, which makes visible only those files or folders that the user has rights to access.  Valid if I(type=cifs).
        type: bool
        default: false
      cifsAuthentications:
        description: A list of share access authentication entries that must be C(present) or C(absent) from the CIFS/SMB share.  Valid if I(type=cifs).
        type: list
        elements: dict
        suboptions:
          name:
            description:
            - The I(name) of the Windows user, group or SID to associate the access requirements with.
            - When checking if a I(name) is C(present), the C(permission) and C(type) fields are also required.
            - When removing items I(state=absent), only the C(name) parameter is needed.
            type: str
          permission:
            description: 
            - Bit representation of the permissions for access authentication.
            - The following values should be used to grant the appropriate access.
            - 0 is no permission
            - 8 is grant read access
            - 24 is grant read and change access
            - 56 is grant read, change and full control
            - 1 is deny read access
            - 3 is deny read and change access
            - 7 is deny read, change and full control
            type: int
          type:
            description: The I(type) of the user/group/SID specified in the C(name) parameter.
            type: str
            choices: ['ALIAS', 'COMPUTER', 'DELETED', 'DOMAIN', 'GROUP', 'INVALID', 'UNKNOWN', 'USER', 'WELLKNOWN']


'''

EXAMPLES = '''
- name: Create HNAS CIFS share
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
  - hv_hnas_share_export:
      state: present
      <<: *login
      data:
        name: "ansible-cifs-share"
        virtualServerId: 2
        filesystemId: "075E7582C745AEA10000000000000000"
        filesystemPath: "\\hello\\frank"
        type: "cifs"
    register: result
  - debug: var=result.cifsShare


- name: Delete HNAS CIFS share
  hosts: localhost
  gather_facts: false
  vars:
    login: &login
      api_url: https://172.27.5.11:8444/v7
      api_key: BgB2qWZVkE.e53OLShtF3If9UIVdTNmvW9dS7ObPqYNPM83OQoeAj9
      validate_certs: false
  tasks:
    - hv_hnas_share_export:
        state: absent
        <<: *login
        data:
          name: "ansible-cifs-share"
          virtualServerId: 2
          type: "cifs"
      register: result
    - debug: var=result.cifsShare

'''

RETURN = '''
[root@localhost ~]# ansible-playbook hv_create_share.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Create HNAS CIFS share] ***********************************************************************************************************************************

TASK [hv_hnas_share_export] *************************************************************************************************************************************
changed: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.cifsShare": {
        "filesystemId": "075E7582C745AEA10000000000000000",
        "name": "ansible-cifs-share",
        "objectId": "323a3a3a35336364653231382d316633322d313164372d393964632d3963353534373037356537353a3a3a303a3a3a4f49445f24232140255f56",
        "path": "\\hello\\frank",
        "settings": {
            "accessConfig": "",
            "cacheOption": "MANUAL_CACHING_DOCS",
            "comment": "",
            "isABEEnabled": false,
            "isFollowGlobalSymbolicLinks": false,
            "isFollowSymbolicLinks": false,
            "isForceFileNameToLowercase": false,
            "isScanForVirusesEnabled": false,
            "maxConcurrentUsers": -1,
            "snapshotOption": "SHOW_AND_ALLOW_ACCESS",
            "transferToReplicationTargetSetting": "USE_FS_DEFAULT",
            "userHomeDirectoryMode": "OFF",
            "userHomeDirectoryPath": ""
        },
        "shareId": "53cde218-1f32-11d7-99dc-9c5547075e75",
        "virtualServerId": 2
    }
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0


[root@localhost ~]# ansible-playbook hv_delete_share.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [Delete HNAS CIFS share] ***********************************************************************************************************************************

TASK [hv_hnas_share_export] *************************************************************************************************************************************
changed: [localhost]

TASK [debug] ****************************************************************************************************************************************************
ok: [localhost] => {
    "result.cifsShare": ""
}

PLAY RECAP ******************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

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
    share = ""
    try:
        assert 'type' in variables, "Missing 'type' data value"
        type = variables['type']
        assert 'virtualServerId' in variables, "Missing 'virtualServerId' data value"
        virtualServerId = variables['virtualServerId']
        assert 'name' in variables, "Missing 'name' data value"
        name = variables['name']
        state = params['state']
        hnas = server.HNASFileServer(api_url, verify=validate_certs)
        hnas.set_credentials(api_key, api_username, api_password)
        if state == "absent":
            changed, share = hnas.delete_share_or_export(virtualServerId, type, variables)
        elif state == "present":
            changed, success, share = hnas.create_share_or_export(virtualServerId, type, variables)
            assert success == True, "An existing share/export exists, with the same name, but the parameters do not match"

    except:
        error = get_exception()
        module.fail_json(msg="HNAS share/export task failed on system at [%s] due of [%s]" % (api_url, str(error)))

    result = dict(changed=changed)
    if type == "nfs":
        result['nfsExport'] = share
    else:
        result['cifsShare'] = share
    module.exit_json(msg="HNAS share/export task completed successfully on system at [%s]" % (hnas.get_address()), **result)

if __name__ == '__main__':
    main()
