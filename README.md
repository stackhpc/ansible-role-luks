[![Build Status](https://travis-ci.com/stackhpc/ansible-role-luks.svg?branch=master)](https://travis-ci.com/stackhpc/ansible-role-luks)

luks
=========

Sets up LUKS encryption.

Requirements
------------

None

Role Variables
--------------

See comments in `defaults/main.yml`.


Dependencies
------------

None

Example Playbooks
-----------------

Generating the encryption keys automatically:

```
- name: Converge
  hosts: all
  vars:
    luks_devices:
      - device: /dev/loop0
        name: cryptotest
  roles:
    - role: stackhpc.luks
```

Using a pre-generated key:

```
- name: Converge
  hosts: all
  vars:
    luks_devices:
      - device: /dev/loop0
        name: cryptotest
        keyfile: /path/to/key/on/ansible/host
  roles:
    - role: stackhpc.luks
```

Tearing down the encrypted device, `cryptotest`:

```
- name: Destroy
  hosts: all
  vars:
    luks_devices:
      - device: /dev/loop0
        name: cryptotest
    luks_action: teardown
  roles:
    - role: stackhpc.luks
```

NOTE: Teardown does not delete the key files or the data. You should
use some other means of doing this if required.

Tearing down all umounted devices:

```
- name: Destroy
  hosts: all
  vars:
    luks_action: teardown-unmounted
  roles:
    - role: stackhpc.luks
```

Testing
-------

Be default, vagrant with the libvirt provider is used for testing. It is possible to run
a reduced set of tests using the docker molecule driver.

To run the vagrant tests you need to install the `python-vagrant`, `molecule` and `ansible` pip
packages.

```
pip install 'molecule<3.0.0' ansible===2.9.6 python-vagrant
```

You will also need to have installed vagrant and the vagrant libvirt provider. For debian
based distributions you can use something like:

```
wget -nv https://releases.hashicorp.com/vagrant/2.2.7/vagrant_2.2.7_x86_64.deb
sudo dpkg -i vagrant_2.2.7_x86_64.deb
vagrant plugin install vagrant-libvirt
```

You can then run the tests using the command:

```
molecule test
```

or to use the docker scenario:

```
molecule test -s docker
```

other scenarios:

- teardown: sets up two encrypted block devices, mounts one, performs a teardown-unmounted

License
-------

Apache

Author Information
------------------

Will Szumski
