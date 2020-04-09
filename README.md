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

License
-------

Apache

Author Information
------------------

Will Szumski
