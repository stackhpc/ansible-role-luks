import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_crypto_devices(host):
    f = host.file('/dev/mapper/cryptotest')
    assert f.exists
    f = host.file('/dev/mapper/cryptotest1')
    assert not f.exists


@pytest.mark.parametrize('file, content, exists', [
    ("/etc/crypttab", "cryptotest /dev/loop0 /etc/luks-keys/dev-loop0", True),
    ("/etc/crypttab", "cryptotest1 /dev/loop1 /etc/luks-keys/dev-loop1", False)
])
def test_crypttab(host, file, content, exists):
    file = host.file(file)
    assert file.exists
    assert file.contains(content) == exists
