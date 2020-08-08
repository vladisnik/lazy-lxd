# Lazy LXD

**Инструмент для простого создания [LXD](https://linuxcontainers.org/lxd/introduction/) контейнеров.**

> С установкой OpenSSH из скрипта, для доступа внутрь по SSH, и выполнения [Ansible](https://www.ansible.com/) playbooks на ними.

## Requirements

- Python >= 3.6
- [LXD](https://linuxcontainers.org/lxd/getting-started-cli/#installation)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) (_Опционально_). Если вы хотите запускать playbooks над созданным контейнером.

## Install

Просто используйте пакетный менеджер [pip](https://pip.pypa.io/en/stable/).

```bash
$ pip install lazy-lxd
```

### Requirements

**LXD**

LXD требуется для основной работы.

Как установить:

apt:
```bash
$ apt install lxd lxd-client
```

snap:
```bash
$ snap install lxd
```

Для centos можно получить инструкцию в следующей [статье](https://discuss.linuxcontainers.org/t/lxd-on-centos-7/1250).
Либо воспользуйтесь snap.

> Для подробной информации см. [официальное руководство](https://linuxcontainers.org/lxd/getting-started-cli).


**Ansible**

Если вы хотите запускать Ansible playbooks из скрипта, нужен предустановленный Ansible.

Python way:
```bash
$ pip install ansible
```

## Usage

Помощь:
```bash
$ lazy-lxd --help
```

Простой контейнер с ОС/версией по умолчанию (_Ubuntu/18.04_):
```bash
$ lazy-lxd
```

### Examples

Контейнер с заданным именем и ОС/версией Centos 6:
```bash
$ lazy-lxd --name centos-container --os centos --release 6
```

Контейнер С ОС/версией Ubuntu 20.04 и заданным путем до директории с вашими Ansible playbooks:
```bash
$ lazy-lxd --os ubuntu --release 20.04 --playbooks-path $HOME/ansible/playbooks
```

Контейнер с заданным именем, ОС/версией по умолчанию и указанием существующих SSH ключей:
```bash
$ lazy-lxd --name ubuntu-focal --ssh-key-private $HOME/.ssh/id_rsa --ssh-key-public $HOME/.ssh/id_rsa.pub
```

## Why script?

Почему не использовать утилиты просто из CLI?

Мне надоело вспоминать синтаксис для запуска lxc, проверять, не занято ли имя контейнера,
каждый раз устанавливать туда OpenSSH, вручную прописывать ключи, ассоциировать его имя с IP адресом контейнера
Все это завернул в одну обертку над всеми этими действиями.

В качестве бонуса, добавлена возможность сразу выполнять существующие Ansible playbooks сразу над созданным контейнером.

## Why LXD?

По моему мнению, [LXD]() лучше подходить для контейнеризации ОС как поле для экспериментов, чем [Docker]().
Удобно возвращаться к одному контейнеру спустя время, не нужно задумываться как хранить данные, что будет если контейнер упадет.
Более statefull, чем Docker контейнеры.

Docker хорошо подходит для изоляции сервиса, запуска 1 процесса на контейнер.
Но не как изоляция ОС для тестов.

## License

Проект использует следующую лицензию: [MIT](LICENSE)
