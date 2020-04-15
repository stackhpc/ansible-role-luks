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
    flat = {}
    parents = []
    indent = 0
    last = None
    for line in lines:
        index = 0
        name = None
        mapping = {'children': [], 'parent': None}
        for col in cols:
            key = col[1]
            value = line[index:index + col[0]]
            if key == "NAME":
                new_indent = len(value) - len(value.lstrip())
                value = value.strip()
                if value.startswith("`-") or value.startswith("|-"):
                    # tree branch counts as indent
                    new_indent += 2
                if new_indent > indent:
                    parents.append(last)
                elif new_indent < indent:
                    parents.pop()
                indent = new_indent
                # Trip off ascii art corresponding to branch, e.g `-
                if value.startswith("`-") or value.startswith("|-"):
                    value = value[2:]
                    mapping["parent"] = parents[-1] if parents else None
                name = value
            else:
                value = value.strip()
            mapping[key] = value
            index += col[0]
        # Children are added to parent entry
        if mapping["parent"]:
            last = mapping["parent"]
            flat[last]["children"].append(mapping)
            flat[name] = mapping
        else:
            flat[name] = mapping
            mappings[name] = mapping
        last = name
    return mappings


def _check_recursive(device):
    results = []
    # We are only interested in mountpoint of leaf nodes
    if device["FSTYPE"] == "crypto_LUKS" and \
            not device["children"][0]["children"]:
        child = device["children"][0]
        if not child["MOUNTPOINT"]:
            entry = {
                "device": "/dev/%s" % device["NAME"],
                "name": child["NAME"]
            }
            results.append(entry)
    else:
        for child in device["children"]:
            result = _check_recursive(child)
            if result:
                results.extend(result)
    return results


def get_unmounted(module):
    _rc, stdout, _stderr = module.run_command("lsblk --fs -i")
    lines = stdout.splitlines()
    mappings = parse_devices(lines[0], lines[1:])
    luks_devices = []
    for master in mappings.values():
        result = _check_recursive(master)
        if result:
            luks_devices.extend(result)
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
