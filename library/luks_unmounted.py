#!/usr/bin/python

# Copyright: (c) 2020, Will Szumski <will@stackhpc.com>
# Licensed under the Apache2 license.

from ansible.module_utils.basic import AnsibleModule
from itertools import islice, takewhile
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: luks_umounted

short_description: Returns all umounted dm-crypt devices.

version_added: "N/A"

description:
    - "Returns all umounted dm-crypt devices."

author:
    - Will Szumski
'''

EXAMPLES = '''
# Retrieve all umounted devices
- name: Determine umounted luks devices
  luks_umounted:
  become: true
  register: result
'''

RETURN = '''
luks_devices:
    description: A list of all umounted dm-crypt devices.
    type: list
    returned: always
'''


def parse_ws(header):
    result = takewhile(lambda x: x.isspace(), header)
    return "".join(result)


def parse_col_name(header):
    result = takewhile(lambda x: not x.isspace(), header)
    return "".join(result)


def parse_header(header):
    """Finds columns in header.
    Result is a list of tuples of the form (length, name)"""
    index = 0
    cols = []
    while index < len(header):
        name = parse_col_name(islice(header, index, None))
        index += len(name)
        ws = parse_ws(islice(header, index, None))
        index += len(ws)
        cols.append((len(name) + len(ws), name))
    return cols


def parse_devices(header, lines):
    """Parses output of lsblk"""
    cols = parse_header(header)
    mappings = {}
    name = None
    for line in lines:
        index = 0
        mapping = {'children': [], 'parent': None}
        for col in cols:
            key = col[1]
            value = line[index:index+col[0]].strip()
            # handle tree structure, child devices start with `-
            if key == "NAME":
                if value.startswith("`-"):
                    value = value[2:]
                    mapping["parent"] = parent
                else:
                    parent = value
                name = value
            mapping[key] = value
            index += col[0]
        # Children are added to parent entry
        if mapping["parent"]:
            parent = mapping["parent"]
            mappings[parent]["children"].append(mapping)
        else:
            mappings[name] = mapping
    return mappings


def get_unmounted(module):
    _rc, stdout, _stderr = module.run_command("lsblk --fs -i")
    lines = stdout.splitlines()
    mappings = parse_devices(lines[0], lines[1:])
    luks_devices = []
    for master in mappings.values():
        if master["FSTYPE"] == "crypto_LUKS":
            for child in master["children"]:
                if not child["MOUNTPOINT"]:
                    entry = {
                        "device": master["NAME"],
                        "name": child["NAME"]
                    }
                    luks_devices.append(entry)
    return luks_devices


def run_module():
    # The module takes no argumnets.
    module_args = dict()

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        luks_devices=[]
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    result['luks_devices'] = get_unmounted(module)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
