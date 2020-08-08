# Lazy LXD

**A tool for easy creating [LXD](https://linuxcontainers.org/lxd/introduction/) containers.**

> Installing OpenSSH right from the script, for accessing into container thru SSH. And running [Ansible](https://www.ansible.com/) playbooks over container.

> Also have Russian language version of [README](README_RU.md)

## Requirements

- Python >= 3.6
- [LXD](https://linuxcontainers.org/lxd/getting-started-cli/#installation)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) (_Optionally_). If you wish to run playbooks over created container.

## Install

Just use the packet manager [pip](https://pip.pypa.io/en/stable/).

```bash
pip install lazy-lxd
```

### Requirements

**LXD**

LXD need to be.

How to install:

apt:
```bash
$ apt install lxd lxd-client
```

snap:
```bash
$ snap install lxd
```

For centos use following [article](https://discuss.linuxcontainers.org/t/lxd-on-centos-7/1250).
Or use snap way.

> For more information see [official guide](https://linuxcontainers.org/lxd/getting-started-cli).

**Ansible**

If you want to run Ansible playbooks over container, you should have installed Ansible.

Python way:
```bash
$ pip install ansible
```

## Usage

Help:
```bash
$ lazy-lxd --help
```

Simple container with default OS/version (_Ubuntu/18.04_):
```bash
$ lazy-lxd
```

### Examples

Container with given name and OS/version is Centos 6:
```bash
$ lazy-lxd --name centos-container --os centos --release 6
```

Container with OS/version is Ubuntu 20.04 and with your path to Ansible playbooks:
```bash
$ lazy-lxd --os ubuntu --release 20.04 --playbooks-path $HOME/ansible/playbooks
```

Container with given name, default OS/version and exists SSH keys:
```bash
$ lazy-lxd --name ubuntu-focal --ssh-key-private $HOME/.ssh/id_rsa --ssh-key-public $HOME/.ssh/id_rsa.pub
```

## Why script?

Why not to user utilities from CLI?

Needs to remember arguments of lxc, check that the container name is free,
set OpenSSH into container every time, create keys manually, doing requests by container IP.
All that this in one wrapper as script.

Run Ansible playbooks from script as bonus.

## Why LXD?

In my opinion, [LXD](https://linuxcontainers.org/lxd/introduction/) is better as container with OS for experiments, than [Docker](https://docs.docker.com/get-started/).
It stateful, shouldn't think about data if container went down.

Docker is better choice for one service per container.
But for OS experiments LXD is better.

## License

This project uses the following license: [MIT](LICENSE)
