#!/usr/bin/python

# Copyright: (c) 2020, Will Szumski <will@stackhpc.com>
# Licensed under the Apache2 license.

from ansible.module_utils.basic import AnsibleModule
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: systemd_escape

short_description: Escapes strings with the systemd-escape utility.

version_added: "N/A"

description:
    - "Returns string as escaped by systemd-escape"

options:
    strings:
        description:
            - List of strings to escape
        type: list

author:
    - Will Szumski
'''

EXAMPLES = '''
# Escapes a list of strings
- name: Escape strings for systemd
  systemd_escape:
    strings:
      - test-string
  register: result
'''

RETURN = '''
escaped:
    description: A dictionary mapping the original string to the escaped string.
    type: dict
    returned: always
'''


def escape(module):
    result = {}
    for string in module.params["strings"]:
        if not isinstance(string, str):
            module.fail_json(
                msg="Received invalid argument. %s is not a string" % string
            )
        _rc, stdout, _stderr = module.run_command(
            ["systemd-escape", string], check_rc=True)
        # NOTE(wszumski): _rc will always be equal to zero here due to check_rc above.
        result[string] = stdout.strip()
    return result


def run_module():

    module_args = {
        "strings": {"type": "list"}
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        luks_devices=[]
    )

    result['escaped'] = escape(module)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
