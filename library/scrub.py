#!/usr/bin/python

# Copyright: (c) 2020, Will Szumski <will@stackhpc.com>
# Licensed under the Apache2 license.

import os
from ansible.module_utils.basic import AnsibleModule
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: scrub

short_description: scrubs a file

version_added: "N/A"

description:
    - "Scrubs a file using the scrub utility"

options:
    path:
        description:
            - Path to file to scrub
        type: path

author:
    - Will Szumski
'''

EXAMPLES = '''
# Scrubs a file
- name: Scrub a file
  scrub:
    path: /tmp/test
'''


def scrub(module):
    result = dict(
        changed=False,
    )
    path = module.params["path"]
    if os.path.exists(path):
        _rc, stdout, stderr = module.run_command(
            ["scrub", "-r", path], check_rc=True)
        # NOTE(wszumski): _rc will always be equal to zero here due to check_rc above.
        result["stdout"] = stdout
        result["stderr"] = stderr
        result["changed"] = True
    return result


def run_module():

    module_args = {
        "path": {"type": "path"}
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        changed=False,
    )

    if module.check_mode:
        module.exit_json(**result)

    result = scrub(module)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
