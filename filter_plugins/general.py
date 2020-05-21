# Copyright (c) 2020 StackHPC Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

from ansible import errors
import jinja2


def _get_hostvar(context, var_name, inventory_hostname=None):
    if inventory_hostname is None:
        namespace = context
    else:
        if inventory_hostname not in context['hostvars']:
            raise errors.AnsibleFilterError(
                "Inventory hostname '%s' not in hostvars" % inventory_hostname)
        namespace = context["hostvars"][inventory_hostname]
    return namespace.get(var_name)


@jinja2.contextfilter
def luks_mode(context, device):
    """Returns a string represent the mode"""
    if "mode" in device:
        return device["mode"]
    return "keyfile"


@jinja2.contextfilter
def luks_key(context, device):
    """Returns name of keyfile"""
    return device["device"].replace('/', '-')[1:]


@jinja2.contextfilter
def luks_keypath(context, device):
    """Returns full path to keyfile"""
    directory = _get_hostvar(context, "luks_keys_path")
    key = luks_key(context, device)
    return os.path.join(directory, key)


class FilterModule(object):
    """Utility filters."""

    def filters(self):
        return {
            'luks_mode': luks_mode,
            'luks_key': luks_key,
            'luks_keypath': luks_keypath,
        }
