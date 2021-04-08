#!/bin/bash
# should check for ansible and check version is 2.9 or above

ANSIBLE_VERSION=`ansible --version | head -1`
echo ${ANSIBLE_VERSION}

# get python folder
PYTHON_PACKAGES=`python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`
echo "Python package location:"
echo "  PYTHON_PACKAGES=\"${PYTHON_PACKAGES}\""

if [ "${PYTHON_PACKAGES}" == "" ]; then
    echo "Failed to find Python package install location, installation aborted"
    exit 1
fi

# should check for module_utils
echo "Ansible module locations:"
ANSIBLE_MODULE_UTILS="${PYTHON_PACKAGES}/ansible/module_utils"
ANSIBLE_MOUDLES="${PYTHON_PACKAGES}/ansible/modules"
echo "  ANSIBLE_MODULE_UTILS=\"${ANSIBLE_MODULE_UTILS}\""
echo "  ANSIBLE_MOUDLES=\"${ANSIBLE_MOUDLES}\""

if [ ! -d "${ANSIBLE_MODULE_UTILS}" ] || [ ! -d  "${ANSIBLE_MOUDLES}" ]; then
    echo "Failed to find Ansible module location, installation aborted"
    exit 1
fi

HV_MODULE_UTILS="${ANSIBLE_MODULE_UTILS}/storage/hv"
HV_MODULES="${ANSIBLE_MOUDLES}/storage/hv"
if [ ! -d "${HV_MODULES}" ]; then
    echo "Creating ${HV_MODULES}"
    mkdir -p "${HV_MODULES}"
fi

if [ ! -d "${HV_MODULE_UTILS}" ]; then
    echo "Creating ${HV_MODULE_UTILS}"
    mkdir "${HV_MODULE_UTILS}"
fi

# number of modules to be installed
MODULE_COUNT=5

echo -e "\nInstalling common module(s)"
\cp -f hv_hnas_main.py ${HV_MODULE_UTILS}
touch ${HV_MODULE_UTILS}/__init__.py

echo "Installing Hitachi NAS Modules"
\cp -f hv_hnas_facts.py ${HV_MODULES}
\cp -f hv_hnas_filesystem.py ${HV_MODULES}
\cp -f hv_hnas_share_export.py ${HV_MODULES}
\cp -f hv_hnas_storage_pool.py ${HV_MODULES}
\cp -f hv_hnas_virtual_server.py ${HV_MODULES}
touch ${HV_MODULES}/__init__.py

INSTALLED_MODULES=`ansible-doc -l | grep hv_hnas`
echo "Installed hv_hnas* modules:"
echo "${INSTALLED_MODULES}"

INSTALLED_MODULE_COUNT=$(wc -l <<< "${INSTALLED_MODULES}")

if [[ $INSTALLED_MODULE_COUNT == 5 ]]; then
    echo "All Hitachi NAS Modules for Ansible successfully installed"
fi

exit 0