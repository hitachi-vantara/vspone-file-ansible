# Hitachi NAS Ansible Collection
This collection provides a series of Ansible modules and plugins for interacting with Hitachi NAS storage systems.

This collection works with Ansible 2.9+, and has been tested with both Python2 and Python3.

Copyright: (c) 2021-2024, Hitachi Vantara, LTD

## Hardware requirements
- Hitachi VSP One File 32, 34, 38
  - Firmware version - NAS File OS v15.1 or higher
- Hitachi NAS 5200, 5300
  - Firmware version - NAS File OS v13.9 or higher
- Hitachi NAS 4060, 4080, 4100
  - Firmware version - NAS File OS v13.7 or higher

## Instructions
- Clone the repository
- CD into the folder of the cloned repository
- Run the following command to build the ansible modules:
``` bash
ansible-galaxy collection build 
```
- once the build has completed, run the following command to install the modules:
```bash
ansible-galaxy collection install hitachivantara-hnas-1.2.0.tar.gz
```
- If upgrading from a previous version of the Hitachi NAS Ansible modules, use the following installation command instead:
```bash
ansible-galaxy collection install --force hitachivantara-hnas-1.2.0.tar.gz
```

To use this collection, add the following to the top of your playbook
```
collections:
  - hitachivantara.hnas
```

**Note:** The collection namespace has been changed.  Any playbooks used with previous versions of this collection will require updating to use the new namespace, and the collection installed within the old namespace should be removed to avoid confusion
```
Old namespace:     hitachi.hnas
Current namespace: hitachivantara.hnas
```

## Modules
The collection is made up from six modules that can view and manage various aspects of Hitachi NAS systems.

### hnas_facts
- This module can be used to gather details about a Hitachi NAS system.  It includes physical details and file serving details.

### hnas_storage_pool
- This module manages Hitachi NAS storage pools.  It allows the creation and deletion of storage pools.  The presence of a storage pool allows filesystems to be created.

### hnas_filesystem
- This module manages Hitachi NAS filesystems.  It can be used to create or delete filesystems.  It can also be used to expand existing filesystems.  Filesystem can also be mounted or unmounted using this module.

### hnas_virtual_server
- This module manages Hitachi NAS virtual servers.  It can be used to ensure that a virtual server does or does not exist. IP addresses can also be added or removed from virtual servers using this module.

### hnas_share_export
- This module manages CIFS/SMB shares and NFS exports on Hitachi NAS servers.  They can be created, deleted or updated.  For CIFS/SMB shares, the share access authentications can also be updated using this module.

### hnas_virtual_volume
- This module allows the creation and deletion of Hitachi NAS virtual volumes.  It also allows the virtual volumes quota to be created and updated.

## Documention

Documentation is available directly from the Hitachi NAS Ansible modules using the following command:
```
ansible-doc hitachivantara.hnas.hnas_facts
```
To view documentaion for others module within the collection, replace ```hnas_facts``` with the name of the module.

For full documenation, see https://docs.hitachivantara.com/v/u/en-us/nas-platform/mk-92hnas096
