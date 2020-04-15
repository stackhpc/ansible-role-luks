# Copyright (c) 2018 StackHPC Ltd.
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

from __future__ import absolute_import
import imp
import os

from tests.utils import ModuleTestCase

# Python 2/3 compatibility.
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch  # noqa

# Import method lifted from kolla_ansible's test_merge_config.py
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
PLUGIN_FILE = os.path.join(PROJECT_DIR, 'library/' 'luks_unmounted.py')

luks_unmounted = imp.load_source('luks_unmounted', PLUGIN_FILE)

sample_1 = """NAME          FSTYPE      FSVER LABEL  UUID                                 FSAVAIL FSUSE% MOUNTPOINT
loop0
sda
|-sda1        vfat        FAT32        40C3-1173                             609.8M    20% /boot
`-sda2        crypto_LUKS 2            607417fa-ac30-4e07-bf3e-0ae133ee9944
  `-cryptroot xfs               rootfs e0b81424-d73f-4114-a872-839374e55f3c    1.3T    29% /
`-sda3        crypto_LUKS 2            607417fa-ac30-4e07-bf3e-0ae133ee9944
  `-test      xfs               test   e0b81424-d73f-4114-a872-839374e55f3c    1.3T    29%
"""  # noqa

sample_2 = """NAME          FSTYPE      LABEL UUID                                 MOUNTPOINT
vda
`-vda1        xfs               8ac075e3-1124-4bb6-bef7-a6811bf8b870 /
loop0         crypto_LUKS       f948def2-4101-416d-81e6-c4ee7d34e59a
`-cryptotest
loop1         crypto_LUKS       6a0f30fc-8145-46bb-8b8e-9f53df717436
`-cryptotest1
"""  # noqa


def unordered_dict_equals(l1, l2):
    return all([x in l2 and y in l1 for x in l1 for y in l2])


class LuksUnmountedTestCase(ModuleTestCase):

    def setUp(self):
        super(LuksUnmountedTestCase, self).setUp()

    def test_sample1(self):
        self.mock_module.run_command = MagicMock(
            return_value=(0, sample_1, "")
        )
        expected = [{
            'device': '/dev/sda3',
            'name': 'test'
        }]
        result = luks_unmounted.get_unmounted(self.mock_module)
        self.assertEqual(expected, result)

    def test_sample2(self):
        self.mock_module.run_command = MagicMock(
            return_value=(0, sample_2, "")
        )
        expected = [{'device': '/dev/loop0', 'name': 'cryptotest'},
                    {'device': '/dev/loop1', 'name': 'cryptotest1'}]
        result = luks_unmounted.get_unmounted(self.mock_module)
        self.assertTrue(unordered_dict_equals(expected, result))
