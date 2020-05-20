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
PLUGIN_FILE = os.path.join(PROJECT_DIR, 'library/' 'luksdump.py')
SAMPLE_DIR = os.path.join(PROJECT_DIR, 'tests', 'samples', 'luksdump')

luksdump = imp.load_source('luksdump', PLUGIN_FILE)


class LuksDumpTestCase(ModuleTestCase):

    def setUp(self):
        super(LuksDumpTestCase, self).setUp()
        with open(os.path.join(SAMPLE_DIR, 'luksv1.txt')) as f:
            self.v1 = f.readlines()
        with open(os.path.join(SAMPLE_DIR, 'luksv2.txt')) as f:
            self.v2 = f.readlines()

    def test_v1parser_keyslots(self):
        expected = [3]
        parser = luksdump.V1Parser(self.v1)
        result = parser.keyslots_used()
        self.assertEqual(expected, result)

    def test_v2parser_keyslots(self):
        expected = [3]
        parser = luksdump.V2Parser(self.v2)
        result = parser.keyslots_used()
        self.assertEqual(expected, result)
