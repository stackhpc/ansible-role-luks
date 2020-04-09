import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_key_files_exist(host):
    f = host.file('/etc/luks-keys/dev-loop0')
    assert f.exists
    f = host.file('/etc/luks-keys/dev-loop1')
    assert f.exists


@pytest.mark.parametrize('file, content', [
    ("/etc/crypttab", "cryptotest /dev/loop0 /etc/luks-keys/dev-loop0"),
    ("/etc/crypttab", "cryptotest1 /dev/loop1 /etc/luks-keys/dev-loop1")
])
def test_crypttab(host, file, content):
    file = host.file(file)
    assert file.exists
    assert file.contains(content)
