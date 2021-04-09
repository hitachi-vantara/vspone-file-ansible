#!/bin/bash

# Function to compare two version strings https://stackoverflow.com/a/24067243/9761984
function versionGreaterThan() { test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"; }

# param 1 = fixed version for comparison
# param 2 = one to check
# returns 0 if the supplied version is NOT greater than the fixed version
function checkVersion()
{
    version=`echo "$2" | cut -d' ' -f2`
    if versionGreaterThan "$1" "$version"; then
        return 0
    fi
    return 1
}

ansible_minimum_version="2.9"

# should check for ansible and check version is 2.9 or above
# should be of the form "ansible 2.9.10"
ansible_version=`ansible --version | head -1`
echo ${ansible_version}

if checkVersion "${ansible_minimum_version}" "${ansible_version}"; then
    echo "Ansible version must be ${ansible_minimum_version} or newer - installation aborted"
    exit 1
fi

# should show where the ansible modules are stored
# should be of the form "  ansible python module location = /usr/lib/python2.7/site-packages/ansible"
ansible_python_packages=`ansible --version | grep "python module location"`
python_packages=`echo "${ansible_python_packages}" | cut -d'=' -f2`
# removes spaces at the beginning of the variable
python_packages=`echo ${python_packages}`
#python_packages=""

if [ "${python_packages}" == "" ]; then
# unable to determine location of pyton packages Ansible is using, so try to work it out, including which version of Python is being used
    echo "Unable to get the Ansible python module location, attempting to work it out.."
    # should be of the form "  python version = 2.7.5 (default, Apr  2 2020, 13:16:51) [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)]"
    ansible_python_version=`ansible --version | grep "python version"`
#ansible_python_version="  python version = 3.1.5 (default, Apr  2 2020, 13:16:51) [GCC 4.8.5 20150623 (Red Hat 4.8.5-39)]"
    echo ${ansible_python_version}
    python_version=`echo "${ansible_python_version}" | cut -d'=' -f2`

    if checkVersion "3" "${python_version}"; then
        echo "  Ansible using python version 2"
        python_packages=`python2 -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`
    else
        echo "  Ansible using python version 3"
        python_packages=`python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'`
    fi
    python_packages="${python_packages}/ansible"
fi

echo "Python package location:"
echo "  python_packages=\"${python_packages}\""

if [ "${python_packages}" == "" ]; then
    echo "Failed to find Python package install location - installation aborted"
    exit 1
fi

# should check for existancce of the Ansible module and module_utils folders
echo "Ansible module locations:"
ansible_module_utils="${python_packages}/module_utils"
ansible_modules="${python_packages}/modules"
echo "  ansible_module_utils=\"${ansible_module_utils}\""
echo "  ansible_modules=\"${ansible_modules}\""

if [ ! -d "${ansible_module_utils}" ] || [ ! -d  "${ansible_modules}" ]; then
    echo "Failed to find Ansible module location, installation aborted"
    exit 1
fi

# If HV specific folders don't exist, create them
hv_module_utils="${ansible_module_utils}/storage/hv"
hv_modules="${ansible_modules}/storage/hv"
if [ ! -d "${hv_modules}" ]; then
    echo "Creating ${hv_modules}"
    mkdir -p "${hv_modules}"
fi

if [ ! -d "${hv_module_utils}" ]; then
    echo "Creating ${hv_module_utils}"
    mkdir "${hv_module_utils}"
fi

common_files=("hv_hnas_main.py" "__init__.py")

echo -e "\nInstalling common modules (${#common_files[@]} files) to ${hv_module_utils}"
for file in "${common_files[@]}"; do
    \cp -f "$file" "${hv_module_utils}"
done

module_files=("hv_hnas_facts.py" "hv_hnas_filesystem.py" "hv_hnas_share_export.py" "hv_hnas_storage_pool.py" "hv_hnas_virtual_server.py" "__init__.py")

echo "Installing Hitachi NAS Modules (${#module_files[@]} files) to ${hv_modules}"
for file in "${module_files[@]}"; do
    \cp -f "$file" "${hv_modules}"
done

installed_modules=`ansible-doc -l | grep hv_hnas`
echo "Installed hv_hnas* modules:"
echo "${installed_modules}"

installed_module_count=$(wc -l <<< "${installed_modules}")

# Check all modules were installed - 1 less than show in the ansible-doc command (__init__.py does not count)
if [[ $installed_module_count == $(( ${#module_files[@]} - 1 )) ]]; then
    echo -e "\nAll Hitachi NAS Modules for Ansible successfully installed"
fi

exit 0
