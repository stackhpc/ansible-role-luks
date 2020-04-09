import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_crypto_devices(host):
    f = host.file('/dev/mapper/cryptotest')
    assert f.exists
    f = host.file('/dev/mapper/cryptotest1')
    assert f.exists
