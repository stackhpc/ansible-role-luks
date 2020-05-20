#!/usr/bin/python

# Copyright: (c) 2020, Will Szumski <will@stackhpc.com>
# Licensed under the Apache2 license.

import itertools
import re

from ansible.module_utils.basic import AnsibleModule
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: luksdump

short_description: Gathers the luks header using luksDump

version_added: "N/A"

description:
    - "Returns the raw luks header and attempts to parse some values."

options:
    path:
        description:
            - Path of device to dump header from
        type: path

author:
    - Will Szumski
'''

EXAMPLES = '''
- name: Dump luks header
  luksdump:
    path: /dev/vdb
  register: result
'''

RETURN = '''
luksdump:
    description: String containing the raw header.
    type: string
    returned: always
keys:
    description: Integers IDs of keyslots that are in use.
    type: list
    returned: always
'''


class Parser(object):
    def __init__(self, luksdump):
        self.luksdump = luksdump


class V1Parser(Parser):

    def keyslots_used(self):
        """Returns keyslots that are in use"""
        prog = re.compile(r"Key Slot (\d+): ENABLED")
        keys = set()
        for line in self.luksdump:
            match = prog.match(line)
            if match:
                keys.add(int(match.group(1)))
        return list(keys)


class V2Parser(Parser):

    def keyslots_used(self):
        """Returns keyslots that are in use"""
        luksdump = self.luksdump
        luksdump = itertools.dropwhile(
            lambda x: not x.startswith("Keyslots:"), luksdump)
        luksdump = itertools.takewhile(
            lambda x: not x.startswith("Tokens:"), luksdump)
        # Drop "Keyslots:" line
        luksdump = list(luksdump)[1:]
        r = re.compile(r"^  (\d+).*$")
        result = set()
        for line in luksdump:
            m = r.match(line)
            if m:
                result.add(int(m.group(1)))
        return list(result)


def luksdump(module):
    """Returns luksdump output"""
    path = module.params["path"]
    _rc, stdout, _stderr = module.run_command(
        ["cryptsetup", "luksDump", path], check_rc=True)
    # NOTE(wszumski): _rc will always be equal to zero here due to check_rc above.
    return stdout.splitlines()


def luks_version(module):
    path = module.params["path"]
    # The luks header has slightly differerent presentation between versions, so
    # it is easier to extract the version information using an external tool.
    rc, _stdout, _stderr = module.run_command(
        ["cryptsetup", "isLuks", "--type", "luks1", path], check_rc=False)
    if rc == 0:
        return 1
    rc, _stdout, _stderr = module.run_command(
        ["cryptsetup", "isLuks", "--type", "luks2", path], check_rc=False)
    if rc == 0:
        return 2
    module.fail_json(msg="Unknown luks version")


def parse(luksdump, version=2):
    """Parses information from luks header"""
    # At the moment we only parse a list of used keyslots as
    # the header is non trivial to parse due to an indentation
    # based presentation (values can span multiple lines).
    result = {
        # We never make any modifications
        "luksdump": "\n".join(luksdump),
        "changed": False
    }
    parser = None
    if version == 2:
        parser = V2Parser(luksdump)
    elif version == 1:
        parser = V1Parser(luksdump)
    result["keyslots"] = parser.keyslots_used()
    return result


def run_module():

    module_args = {
        "path": {"type": "path"}
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    version = luks_version(module)
    dump = luksdump(module)
    result = parse(dump, version=version)
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
