
# Copyright: (c) 2021, Hitachi Vantara, LTD

import json
import requests
import re
import time

class HNASFileServer:

# api_url is a standard Ansible parameter - required form https://172.27.1.1:8444/v7
    def __init__(self, api_url, verify=True):
        p = re.compile(r'(?P<protocol>http[s]?)://(?P<address>[0-9a-zA-Z.-]+):(?P<port>\d+)/v(?P<version>\d)')
        m = p.match(api_url)
        assert m != None, "api_url is not of the correct format - http[s]://<address>:<port>/v<api-version>"
        self.protocol = m.group('protocol')
        self.address = m.group('address')
        self.port = m.group('port')
        self.version = m.group('version')
        self.base_uri = "{}://{}:{}/v{}/storage/".format(self.protocol, self.address, self.port, self.version)
        self.verify = verify
        self.headers = {}
        self.headers['Content-Type'] = 'application/json'

    def set_credentials(self, api_key=None, api_username=None, api_password=None):
        self.api_key = api_key
        self.api_username = api_username
        self.api_password = api_password
        if self.api_key == None:
            self.headers["X-Subsystem-User"] = self.api_username
            self.headers["X-Subsystem-Password"] = self.api_password
        else:
            self.headers["X-Api-Key"] = self.api_key

    def get_address(self):
        return self.address
        
    def append_to_url(self, url, parameter):
        if url.find('?') == -1:
            new_url = ''.join([url, '?'])
        else:
            new_url = ''.join([url, '&'])
        return ''.join([new_url, parameter])

# message should be in json format
    def get_error_details(self, response):
        try:
            message = response.json()
            error = message['errorMsg']
            if 'errorDetail' in message:
                return ' - '.join([error, message['errorDetail']['message']])
        except:
            error = "No details"
        return error

    def check_share_export_type(self, type):
        assert type == "nfs" or type == "cifs", "Unsupported share type '{}' supplied - must be 'cifs' or 'nfs'".format(type)

    def check_share_export_name(self, type, name):
        self.check_share_export_type(type)
# shouldn't need to do anything with a cifs name
        if name == None:
            return None
        if type == "cifs":
            return name
        if name.startswith('/'):
            return name
        return ''.join(['/', name])

# params are supplied by the user in the yml file
# param_list is a list of needed parameters
# description is text to return as part of the error message
    def check_required_parameters(self, params, param_list, description=""):
        for item in param_list:
            assert item in params, "Missing \'{}\' parameter.  {}".format(item, description)
        return

    def simple_get(self, url):
        response = requests.get(url, headers=self.headers, verify=self.verify)
        assert response.status_code == 200, "{} {} - {}".format(response.status_code, response.reason, self.get_error_details(response))
        return response.json()

    def simple_post(self, url, expected_status_code, data=None):
        response = requests.post(url, headers=self.headers, json=data, verify=self.verify, allow_redirects=False)
        assert response.status_code == expected_status_code, "{} {} - {}".format(response.status_code, response.reason, self.get_error_details(response))
        if response.text != "":
            return response.json()
        return None

    def simple_patch(self, url, expected_status_code, data=None):
        response = requests.patch(url, headers=self.headers, json=data, verify=self.verify, allow_redirects=False)
        assert response.status_code == expected_status_code, "{} {} - {}".format(response.status_code, response.reason, self.get_error_details(response))
        if response.text != "":
            return response.json()
        return None

    def simple_delete(self, url):
        response = requests.delete(url, headers=self.headers, verify=self.verify)
        assert response.status_code == 204, "{} {} - {}".format(response.status_code, response.reason, self.get_error_details(response))
        
    def get_unit_multiplier(self, unit):
        unit = unit.lower()
        if unit == "b" or unit == "bytes":
            return 1
        if unit == "k" or unit == "kb":
            return 1000
        if unit == "kib":
            return 1024
        if unit == "m" or unit == "mb":
            return 1000 * 1000
        if unit == "mib":
            return 1024 * 1024
        if unit == "g" or unit == "gb":
            return 1000 * 1000 * 1000
        if unit == "gib":
            return 1024 * 1024 * 1024
        if unit == "t" or unit == "tb":
            return 1000 * 1000 * 1000 * 1000
        if unit == "tib":
            return 1024 * 1024 * 1024 * 1024
        return 1

    def get_file_server_info(self):
        return self.simple_get(self.base_uri + "file-devices")

    def get_nodes(self):
        return self.simple_get(self.base_uri + "nodes")

    def get_virtual_servers(self, virtualServerId=None, name=None):
        url = self.base_uri + "virtual-servers"
        if virtualServerId != None:
            url = self.append_to_url(url, "virtualServerId={}".format(virtualServerId))
        if name != None:
            url = self.append_to_url(url, "name={}".format(name))
        return self.simple_get(url)

    def get_file_systems(self, virtualServerId=None, label=None):
        url = self.base_uri + "filesystems"
        if virtualServerId != None:
            url = self.append_to_url(url, "virtualServerId={}".format(virtualServerId))
        if label != None:
            url = self.append_to_url(url, "label={}".format(label))
        return self.simple_get(url)
    
    def get_file_system(self, filesystemId):
        url = self.base_uri + "filesystems/{}".format(filesystemId)
        return self.simple_get(url)

    def get_share_or_export(self, virtualServerId, type, name=None):
        name = self.check_share_export_name(type, name)
        url = self.base_uri + "virtual-servers/{}/{}".format(virtualServerId, type)
        if name != None:
            url = self.append_to_url(url, "name={}".format(name))
        share_list = self.simple_get(url)
        if type == "cifs":
            for share in share_list['filesystemShares']:
                saa_list = self.get_cifs_authentications(share['objectId'])
                share['cifsAuthentications'] = saa_list.get('cifsAuthentications', dict())
        return share_list

    def get_shares(self, virtualServerId, name=None):
        return self.get_share_or_export(virtualServerId, "cifs", name=name)

    def get_exports(self, virtualServerId, name=None):
        return self.get_share_or_export(virtualServerId, "nfs", name=name)

    def get_system_drives(self):
        return self.simple_get(self.base_uri + "system-drives")

    def get_storage_pools(self, storagePoolId=None, label=None):
        url = self.base_uri + "storage-pools"
        if storagePoolId != None:
            url = self.append_to_url(url, "storagePoolId={}".format(storagePoolId))
        if label != None:
            url = self.append_to_url(url, "label={}".format(label))
        return self.simple_get(url)

    def get_snapshots(self, filesystemId):
        return self.simple_get(self.base_uri + "filesystem-snapshots/{}/null".format(filesystemId))

# physical or aggregate interfaces
    def get_network_interfaces(self, physical=False):
        ports = []
        for item in self.simple_get(self.base_uri + "file-devices/ethernet-interfaces")["ethernetInterfaces"]:
            if physical == True and item["isAggregationAllowed"] == True:
                ports.append(item["name"])
            elif physical == False and item["isVirtualServerIpAllowed"] == True:
                ports.append(item["name"])
        return dict(ports=ports)

# return True if the share was deleted, False if it was not present
# return <changed> <share>
    def delete_share_or_export(self, virtualServerId, type, params):
        self.check_required_parameters(params, ['name'])
        name = self.check_share_export_name(type, params['name'])
        share_list = self.get_share_or_export(virtualServerId, type, name)
        if len(share_list['filesystemShares']) == 0:  # not there anyway, so can be considered absent
            return False, ""
        share = share_list['filesystemShares'][0]
        if type == 'cifs' and 'cifsAuthentications' in params:
        # delete cifs saa instead of the share
            changed = self.delete_cifs_authentications(share['objectId'], params)
            saa_list = self.get_cifs_authentications(share['objectId'])
            share['cifsAuthentications'] = saa_list.get('cifsAuthentications', dict())
        else:
            url = self.base_uri + "filesystem-shares/{}/{}".format(type, share['objectId'])
            self.simple_delete(url)
            changed = True
            share = ""
        return True, share

# share/export specific parameters are in the params dictionary
# returns three values <changed> <success> <share>
    def create_share_or_export(self, virtualServerId, type, params):
        self.check_share_export_type(type)
        data = {}
        data['virtualServerId'] = virtualServerId
        self.check_required_parameters(params, ['name', 'filesystemId'])
        data['name'] = self.check_share_export_name(type, params['name'])
        data['filesystemId'] = params['filesystemId']
        settings = {}
# check to see if it already exists on the same virtual server
        share_list = self.get_share_or_export(virtualServerId, type, data['name'])
        if len(share_list['filesystemShares']) != 0:  # already there, so can be considered present
            share = share_list['filesystemShares'][0]
# only parameters that stay constant are the name, virtualServerId and filesystemId - all others can be changed
            if share['filesystemId'] == data['filesystemId']:
                existing_settings = share['settings']
                update_needed = False
                data['filesystemPath'] = params.get('filesystemPath', share['path'])
                settings['accessConfig'] = params.get('accessConfig', existing_settings['accessConfig'])
                settings['snapshotOption'] = params.get('snapshotOption', existing_settings['snapshotOption'])
                settings['transferToReplicationTargetSetting'] = params.get('transferToReplicationTargetSetting', existing_settings['transferToReplicationTargetSetting'])
                if type == "nfs":
                    settings['localReadCacheOption'] = params.get('localReadCacheOption', existing_settings['localReadCacheOption'])
                elif type == 'cifs':
                    settings['comment'] = params.get('comment', existing_settings['comment'])
                    settings['userHomeDirectoryPath'] = params.get('userHomeDirectoryPath', existing_settings['userHomeDirectoryPath'])
                    settings['isScanForVirusesEnabled'] = params.get('isScanForVirusesEnabled', existing_settings['isScanForVirusesEnabled'])
                    settings['maxConcurrentUsers'] = params.get('maxConcurrentUsers', existing_settings['maxConcurrentUsers'])
                    settings['cacheOption'] = params.get('cacheOption', existing_settings['cacheOption'])
                    settings['userHomeDirectoryMode'] = params.get('userHomeDirectoryMode', existing_settings['userHomeDirectoryMode'])
                    settings['isFollowSymbolicLinks'] = params.get('isFollowSymbolicLinks', existing_settings['isFollowSymbolicLinks'])
                    settings['isFollowGlobalSymbolicLinks'] = params.get('isFollowGlobalSymbolicLinks', existing_settings['isFollowGlobalSymbolicLinks'])
                    settings['isForceFileNameToLowercase'] = params.get('isForceFileNameToLowercase', existing_settings['isForceFileNameToLowercase'])
                    settings['isABEEnabled'] = params.get('isABEEnabled', existing_settings['isABEEnabled'])
# check for any changes to any settings
                if (settings['accessConfig'] != existing_settings['accessConfig'] or settings['snapshotOption'] != existing_settings['snapshotOption'] or
                    settings['transferToReplicationTargetSetting'] != existing_settings['transferToReplicationTargetSetting'] or
                    data['filesystemPath'] != share['path']):
                    update_needed = True
                if (type == "cifs" and (settings['comment'] != existing_settings['comment'] or settings['userHomeDirectoryPath'] != existing_settings['userHomeDirectoryPath'] or
                    settings['isScanForVirusesEnabled'] != existing_settings['isScanForVirusesEnabled'] or 
                    settings['maxConcurrentUsers'] != existing_settings['maxConcurrentUsers'] or settings['cacheOption'] != existing_settings['cacheOption'] or
                    settings['userHomeDirectoryMode'] != existing_settings['userHomeDirectoryMode'] or 
                    settings['isFollowSymbolicLinks'] != existing_settings['isFollowSymbolicLinks'] or 
                    settings['isFollowGlobalSymbolicLinks'] != existing_settings['isFollowGlobalSymbolicLinks'] or 
                    settings['isForceFileNameToLowercase'] != existing_settings['isForceFileNameToLowercase'] or 
                    settings['isABEEnabled'] != existing_settings['isABEEnabled'])):
                    update_needed = True
                if type == "nfs" and settings['localReadCacheOption'] != existing_settings['localReadCacheOption']:
                    update_needed = True
                if update_needed == True:
                    data['settings'] = settings
                    url = self.base_uri + "filesystem-shares/{}/{}".format(type, share['objectId'])
                    self.simple_patch(url, 204, data=data)
                    share_list = self.get_share_or_export(virtualServerId, type, data['name'])
                    share = share_list['filesystemShares'][0]
# should see if SAA list needs to be added to
                if type == 'cifs':
                    if self.add_cifs_authentications(share['objectId'], params):
                        update_needed = True
                    saa_list = self.get_cifs_authentications(share['objectId'])
                    share['cifsAuthentications'] = saa_list.get('cifsAuthentications', dict())
                return update_needed, True, share
            else:
# need to return a failure if a share exists with the same name, virtualServerId, but is hosted on a different filesystem
# REST API allows filesystem to be changed, but don't allow it here
                return False, False, share
# not present, so create it instead
        self.check_required_parameters(params, ['filesystemPath'])
        data['filesystemPath'] = params['filesystemPath']
        settings['accessConfig'] = params.get('accessConfig', "")
        settings['snapshotOption'] = params.get('snapshotOption', "SHOW_AND_ALLOW_ACCESS")
        settings['transferToReplicationTargetSetting'] = params.get('transferToReplicationTargetSetting', "USE_FS_DEFAULT")
        if type == "nfs":
            # need to remove / from beginning of NFS export due to legacy API bug in create operation, native API does not have the issue
            if data['name'][0] == '/':
                data['name'] = data['name'][1:]
            settings['localReadCacheOption'] = params.get('localReadCacheOption', "DISABLED")
        elif type == "cifs":
            settings['comment'] = params.get('comment', "")
            settings['userHomeDirectoryPath'] = params.get('userHomeDirectoryPath', "")
            settings['isScanForVirusesEnabled'] = params.get('isScanForVirusesEnabled', False)
            settings['maxConcurrentUsers'] = params.get('maxConcurrentUsers', -1)
            settings['cacheOption'] = params.get('cacheOption', "MANUAL_CACHING_DOCS")
            settings['userHomeDirectoryMode'] = params.get('userHomeDirectoryMode', "OFF")
            settings['isFollowSymbolicLinks'] = params.get('isFollowSymbolicLinks', False)
            settings['isFollowGlobalSymbolicLinks'] = params.get('isFollowGlobalSymbolicLinks', False)
            settings['isForceFileNameToLowercase'] = params.get('isForceFileNameToLowercase', False)
            settings['isABEEnabled'] = params.get('isABEEnabled', False)
        data['settings'] = settings

        url = self.base_uri + "filesystem-shares/{}".format(type)
        share = self.simple_post(url, 201, data=data)['filesystemShare']
        if type == "cifs":
# add SAA is specified
            self.add_cifs_authentications(share['objectId'], params)
            saa_list = self.get_cifs_authentications(share['objectId'])
            share['cifsAuthentications'] = saa_list.get('cifsAuthentications', dict())
        return True, True, share

    def set_vitrual_server_state(self, virtualServerId=None, name=None, state=None):
        evs_list = self.get_virtual_servers(virtualServerId, name)
        assert len(evs_list['virtualServers']) != 0, "virtual server not found"
        evs = evs_list['virtualServers'][0]
        if state == evs['status']:
            return True
        if state == 'ONLINE':
            url = self.base_uri + "virtual-servers/{}/enable".format(evs['objectId'])
        elif state == 'DISABLED':
            url = self.base_uri + "virtual-servers/{}/disable".format(evs['objectId'])
        else:
            raise "Invalid 'state' value {} - not valid".format(state)
        self.simple_post(url, 204)
        return True

    def delete_virtual_server_address(self, virtualServerId, address):
        url = self.base_uri + "virtual-servers/{}/ip-addresses/{}".format(virtualServerId, address)
        self.simple_delete(url)
        return True

# deletes a virtual server, or if ipAddres specified, it deletes the address from the virtual server
# return three values <changed> <success> <evs>
    def delete_virtual_server(self, virtualServerId=None, name=None, params=None):
        changed = False
        evs_list = self.get_virtual_servers(virtualServerId, name)
        if len(evs_list['virtualServers']) == 0:    # not there anyway, so can be considered absent
            return changed, True, ""
        evs = evs_list['virtualServers'][0]
        virtualServerId = evs['virtualServerId']
        if 'address_details' in params and len(params['address_details']) > 0:
            success = True
            for address in params['address_details']:                # walk around each one and check it's there
                address_to_remove = address.get('address', "255.255.255.255")
                if address_to_remove in evs['ipAddresses']:          # IP address present, so delete it
                    if len(evs['ipAddresses']) > 1:                  # will only attempt delete if not the last address
                        self.delete_virtual_server_address(virtualServerId, address_to_remove)
                        evs['ipAddresses'].remove(address_to_remove)
                        changed = True
                    else:                                            # can't remove the last address, so fail
                        success = False
            evs_list = self.get_virtual_servers(virtualServerId=virtualServerId)
            evs = evs_list['virtualServers'][0]
            return changed, success, evs
# evs can only be deleted if it's disabled - any filesystems will be unmounted and unassigned, so not deleted
        self.set_vitrual_server_state(virtualServerId=virtualServerId, name=name, state='DISABLED')
        url = self.base_uri + "virtual-servers/{}".format(virtualServerId)
        self.simple_delete(url)
        changed = True
        return changed, True, ""

# adds an IP address to a virtual server
    def add_vitual_server_address(self, virtualServerId=None, name=None, params=None):
        evs_list = self.get_virtual_servers(virtualServerId, name)
        assert len(evs_list['virtualServers']) != 0, "virtual server not found"
        evs = evs_list['virtualServers'][0]
        self.check_required_parameters(params, ['address', 'netmask', 'port'])
        data = {}
        data['ipAddress'] = params['address']
        data['mask'] = params['netmask']
        data['port'] = params['port']
        url = self.base_uri + "virtual-servers/{}/ip-addresses".format(evs['virtualServerId'])
        self.simple_post(url, 204, data=data)

# evs specific parameters are in the params dictionary
# returns three values <changed> <success> <evs>
    def create_virtual_server(self, params):
        data = {}
        self.check_required_parameters(params, ['name'])
        data['name'] = params['name']
        data['clusterNodeId'] = int(params.get('clusterNodeId', 1))
        status = params.get('status', 'ONLINE')
# if address_details are supplied, make sure there is at least one address
        if 'address_details' in params and len(params['address_details']) > 0:
            if 'address' in params['address_details'][0]:
                data['ipAddress'] = params['address_details'][0]['address']
            if 'netmask' in params['address_details'][0]:
                data['netmask'] = params['address_details'][0]['netmask']
            if 'port' in params['address_details'][0]:
                data['ethernetLinkAggregation'] = params['address_details'][0]['port']
        changed = False
        evs_list = self.get_virtual_servers(name=data['name'])
        if len(evs_list['virtualServers']) != 0:            # already there, so can be considered present
            evs = evs_list['virtualServers'][0]
        else:                                               # not present, so create
# should get the fist IP address in the list to use
            assert 'ipAddress' in data, "Missing 'address' parameter from 'address_details' data value"
            assert 'netmask' in data, "Missing 'netmask' parameter from 'address_details' data value"
            assert 'ethernetLinkAggregation' in data, "Missing 'port' parameter from 'address_details' data value"
            url = self.base_uri + "virtual-servers"
            evs = self.simple_post(url, 201, data=data)['virtualServer']
            changed = True
        virtualServerId=evs['virtualServerId']
# walk around each address in the list and check if it's there or not - if not create it
        if 'address_details' in params:                              # some IP address details supplied, so check they are all there
            for address in params['address_details']:                # walk around each one and check it's there
                if address['address'] not in evs['ipAddresses']:     # IP address not already assigned to evs, so add
                    self.add_vitual_server_address(virtualServerId=virtualServerId, params=address)
                    changed = True
        if evs['status'] != status:                          # not correct status, so change
            self.set_vitrual_server_state(virtualServerId=virtualServerId, state=status)
            changed = True
        if changed == True:
            evs_list = self.get_virtual_servers(virtualServerId=virtualServerId)
            evs = evs_list['virtualServers'][0]
        return changed, True, evs

    def set_filesystem_state(self, filesystemId=None, label=None, state=None):
        if filesystemId != None:
            fs = self.get_file_system(filesystemId)['filesystem']
        else:
            fs_list = self.get_file_systems(label=label)[0]
            assert len(fs_list['filesystems']) != 0, "filesystem not found"
            fs = fs_list['filesystems'][0]
        if state == fs['status']:
            return True
        if state == 'MOUNTED':
            url = self.base_uri + "filesystems/{}/mount".format(fs['objectId'])
        elif state == 'NOT_MOUNTED':
            url = self.base_uri + "filesystems/{}/unmount".format(fs['objectId'])
        else:
            raise "Invalid 'state' value {} - not valid".format(state)
        self.simple_post(url, 204)
        self.wait_for_filesystem(filesystemId, state)
        return True

    def wait_for_filesystem(self, filesystemId, required_status):
        """
        Wait until the filesystem gets to a specific status
        - wait for mount/unmount mainly
        """
        url = self.base_uri + "filesystems/{}".format(filesystemId)
        current_status = ""
        count = 0
        while current_status != required_status and count < 30:
            time.sleep(1)
            response = self.simple_get(url)
            current_status = response['filesystem']['status']
            if current_status == "VOLUME_NOT_AVAILABLE_TO_BS":
                break
            count += 1
        assert count != 30, "Waited 30 seconds for file system status to be {} - giving up".format(required_status)

    def format_filesystem(self, filesystemId, blockSize):
        url = self.base_uri + "filesystems/{}/format".format(filesystemId)
        format_data = {'blockSize': blockSize}
        self.simple_post(url, 204, data=format_data)
        return True
        
    def expand_filesystem(self, filesystemId, capacity):
        url = self.base_uri + "filesystems/{}/expand".format(filesystemId)
        format_data = {'capacity': capacity}
        self.simple_post(url, 204, data=format_data)
        return True

    def delete_filesystem(self, label):
        fs_list = self.get_file_systems(label=label)
        if len(fs_list['filesystems']) == 0:  # not there, so can be considered absent
            return False
        fs = fs_list['filesystems'][0]
        filesystemId = fs['objectId']
# need to unmount filesystem before it can be deleted
        self.set_filesystem_state(filesystemId, state="NOT_MOUNTED")
        url = self.base_uri + "filesystems/{}".format(filesystemId)
        self.simple_delete(url)
        return True

# filesystem specific parameters are in the params dictionary
# returns three values <changed> <success> <filesystem>
    def create_filesystem(self, params):
        data = {}
        self.check_required_parameters(params, ['label', 'capacity'])
        data['label'] = params['label']
        if 'virtual_server_name' in params:
            # need to get virtualServerId if name supplied
            evs_list = self.get_virtual_servers(name=params['virtual_server_name'])
            assert len(evs_list['virtualServers']) != 0, "virtual server not found"
            data['virtualServerId'] = evs_list['virtualServers'][0]['virtualServerId']
        else:
            assert 'virtualServerId' in params, "Missing 'virtualServerId' data value"
            data['virtualServerId'] = params['virtualServerId']
        if 'storage_pool_name' in params:
            # need to get storagePoolId if name supplied
            pool_list = self.get_storage_pools(label=params['storage_pool_name'])
            assert len(pool_list['storagePools']) != 0, "storage pool not found"
            data['storagePoolId'] = pool_list['storagePools'][0]['storagePoolId']
        else:
            assert 'storagePoolId' in params, "Missing 'storagePoolId' data value"
            data['storagePoolId'] = params['storagePoolId']
        data['capacity'] = self.get_unit_multiplier(params.get('capacity_unit', 'bytes')) * int(params['capacity'])
        status = params.get('status', 'MOUNTED')
        blockSize = params.get('blockSize', '4')
        blockSizeInK = str(int(blockSize) * 1024)

        changed = False
        fs_list = self.get_file_systems(label=data['label'])
        if len(fs_list['filesystems']) != 0:             # already there, so can be considered present
            fs = fs_list['filesystems'][0]
        else:                                            # not present, so create
            url = self.base_uri + "filesystems"
            fs = self.simple_post(url, 201, data=data)['filesystem']
            changed = True
        filesystemId = fs['objectId']
        if int(fs['blockSize']) == 0:                    # not formatted, so can format it
            self.format_filesystem(filesystemId, blockSize)
            changed = True
        elif int(blockSizeInK) != int(fs['blockSize']):  # block size is different - will not reformat to change the block size - customer data loss
            return changed, False, None
        if status != fs['status']:                       # not correct status, so change
            self.set_filesystem_state(filesystemId, state=status)
            changed = True
        if data['capacity'] > fs['capacity']:            # capacity lower than size, so can expand
            self.expand_filesystem(filesystemId, data['capacity'])
            changed = True
        if changed == True:
            fs = self.get_file_system(filesystemId)['filesystem']
        return changed, True, fs

    def delete_storage_pool(self, label):
        pool_list = self.get_storage_pools(label=label)
        if len(pool_list['storagePools']) == 0:  # not there, so can be considered absent
            return False
        pool = pool_list['storagePools'][0]
        storagePoolId = pool['objectId']
        url = self.base_uri + "storage-pools/{}".format(storagePoolId)
        self.simple_delete(url)
        return True

# storage pool specific parameters are in the params dictionary
# returns three values <changed> <success> <pool>
    def create_storage_pool(self, params):
        data = {'systemDrives':[]}
        self.check_required_parameters(params, ['label'])
        data['label'] = params['label']
        data['chunkSize'] = params.get('chunkSize', 19327352832) # appears to be the default chunk size value
        assert len(params['systemDrives']) >= 4, "Need a minimum of 4 system drives to create a storage pool"
# make sure each system drive is an integer value
        for drive in params['systemDrives']:
            data['systemDrives'].append(int(drive))
        pool_list = self.get_storage_pools(label=params['label'])
        if len(pool_list['storagePools']) != 0:  # already there, so can be considered present
            pool = pool_list['storagePools'][0]
# should get list of system drives, and compare
            if 'chunkSize' in params and pool['chunkSize'] != data['chunkSize']:
                return False, False, ""
            url = self.base_uri + "storage-pools/{}/system-drives".format(pool['objectId'])
            sd_list = self.simple_get(url)
            if len(sd_list['systemDrives']) != len(data['systemDrives']):
                return False, False, ""
# need to check that the system drives are the same
            for drive in sd_list['systemDrives']:
                if int(drive['systemDriveId']) not in data['systemDrives']:
                    return False, False, ""
            return False, True, pool
# need to check if access needs to be allowed to the system drives

# should maybe add this check before checking for the pool, as allowing access might make the pool appear
######################################
# This needs to be improved or removed
        for systemDriveId in data['systemDrives']:
            url = self.base_uri + "system-drives?systemDriveId={}".format(systemDriveId)
            sd_list = self.simple_get(url)
            assert len(sd_list['systemDrives']) != 0, "system drive not found '{}'".format(systemDriveId)
            system_drive = sd_list['systemDrives'][0]
            assert system_drive['isAssignedToStoragePool'] == False, "system drive '{}' already in use".format(systemDriveId)
            if 'allow_denied_system_drives' in params and params['allow_denied_system_drives'] is True and system_drive['isAccessAllowed'] == False:
                url = self.base_uri + "system-drives/{}".format(systemDriveId)
                sd_data = {'enableAccess':True}
                self.simple_patch(url, 204, data=sd_data)
# need to create new pool
        url = self.base_uri + "storage-pools"
        pool = self.simple_post(url, 201, data=data)['storagePool']
        return True, True, pool

    def get_cifs_authentications(self, shareId):
        url = self.base_uri + "filesystem-shares/cifs/{}/authentications".format(shareId)
        return self.simple_get(url)

# need to be able to check the names in a more intelligent way rather than just compare
# return <present> <same permission> <encodedName>
    def is_saa_present(self, saa_list, check_saa):
        for saa in saa_list:
            if check_saa['name'] == saa['name'] or saa['name'].lower().endswith(check_saa['name'].lower()):
                if 'permission' in check_saa and check_saa['permission'] == saa['permission']:
                    return True, True, saa['encodedName']
                else:
                    return True, False, saa['encodedName']
        return False, False, ""
        
# return False if none were added
# return True if some were added i.e. changed
    def add_cifs_authentications(self, shareId, params):
        changed = False
        if 'cifsAuthentications' not in params:
            return changed
        saa_list = self.get_cifs_authentications(shareId)['cifsAuthentications']
# need to walk around the list of existing ones and see if they are present already, as the correct permissions
        new_saa_list = params['cifsAuthentications']
        for saa in new_saa_list:
            present, same, encodedName = self.is_saa_present(saa_list, saa)
            if present == True and same == False:
            # remove existing if the permissions do not match, as it's not possible to update them
                url = self.base_uri + "filesystem-shares/cifs/{}/authentications/{}".format(shareId, encodedName)
                self.simple_delete(url)
                present = False
            if present == False:
            # not there so add it - easier to add them one at time
                url = self.base_uri + "filesystem-shares/cifs/{}/authentications".format(shareId)
                data = {'cifsAuthentications':[]}
                data['cifsAuthentications'].append(saa)
                self.simple_post(url, 201, data=data)
                changed = True
        return changed
        
    def delete_cifs_authentications(self, shareId, params):
        saa_list = self.get_cifs_authentications(shareId)['cifsAuthentications']
        delete_saa_list = params['cifsAuthentications']
        changed = False
        for saa in delete_saa_list:
            present, _, encodedName = self.is_saa_present(saa_list, saa)
            if present == True:
                url = self.base_uri + "filesystem-shares/cifs/{}/authentications/{}".format(shareId, encodedName)
                self.simple_delete(url)
                changed = True
        return changed
