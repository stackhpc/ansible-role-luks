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

Tang/clevis
------------

You can run a tang server with:

```
docker run -d -p 8080:80 -v $(pwd)/persistent:/var/db/tang malaiwah/tang
```

An example playbook, setting the `mode` to `tang`:

```
- name: Converge
  hosts: all
  vars:
    luks_devices:
      - device: /dev/vdb
        name: cryptotest
        mode: tang
        tang_server: 192.168.121.1:8080
        tang_adv: path/to/adv
  roles:
    - role: stackhpc.luks
```

You can retrive the `adv` file by running:

```
curl 192.168.121.1:8080/adv -O
```

This is used to verify the server identity.

Trusted Platform Module (TPM)
-----------------------------

Clevis also supports using a motherboard TPM, version 2.  The process
is simlar to using Tang.

For example:

```
- hosts: compute
  vars:
    luks_devices:
      - name: nvme_crypt
	device: /dev/md0
	mode: tpm2
	tpm2_remove_key: false
	options: ["force"]
```

Initrd Interaction
==================

Setting options for `/etc/crypttab` can be useful if an encrypted
device should be unlocked during the initial ramdisk, before the rootfs
is mounted.  Dracut interprets the `force` option as enforcing the
inclusion of details of this encrypted device in the ramdisk `crypttab`

After constructing LUKS encrypted devices, the ramdisk image should be
regenerated.

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
