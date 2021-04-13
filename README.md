# Hitachi NAS Ansible Collection
This collection provides a series of Ansible modules and plugins for interacting with Hitachi NAS storge systems.

This collection works with Ansible 2.9+

# Installation
```bash
ansible-galaxy collection install hv-hnas-1.0.0.tar.gz
```
To use this collection, add the following to the top of your playbook
```
collections:
  - hitachi.hnas
```

# Modules
The collection is made up from five modules that can manage various aspects of Hitachi NAS systems.

## hnas_facts
This module can be used to gather details about an HNAS system.  It includes physical details and file serving details.

## hnas_storage_pool
This module manages Hitachi NAS storage pools.  It allows the creation and deletion of storage pools.  The presence of a storage pool allows filesystems to be created.

## hnas_filesystem
This module manages Hitachi NAS filesystems.  It can be used to create or delete filesystems.  It can also be used to expand existing filesystems.  Filesystem can also be mounted or unmounted using this module.

## hnas_virtual_server
This module manages Hitachi NAS virtual servers.  It can be used to ensure that a virtual server does or does not exist. IP addresses can also be added or removed from virtual servers using this module.

## hnas_share_export
This module manages CIFS/SMB shares and NFS exports on Hitachi NAS servers.  They can be created, deleted or updated.  For CIFS/SMB shares, the share access authentications can also be updated using this module.
