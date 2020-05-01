import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_crypto_devices(host):
    f = host.file('/dev/mapper/cryptotest')
    assert f.exists


def test_key_files_exist(host):
    f = host.file('/etc/luks-keys/dev-vdb')
    assert not f.exists


@pytest.mark.parametrize('file, content', [
    ("/etc/crypttab", "cryptotest /dev/vdb none _netdev"),
])
def test_crypttab(host, file, content):
    file = host.file(file)
    assert file.exists
    assert file.contains(content)
