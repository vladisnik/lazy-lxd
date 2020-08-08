#!/usr/bin/env python3

"""
Lazy-LXD: Easy Create LXD Container And Run Asible Playbooks Over It.

This module contains the main logic to create container
and running ansible playbooks over it.
"""

import os
import sys
import argparse
import subprocess
import logging
from shutil import which

from lib.lxd import LXDClient
from lib.ansible import AnsibleClient
from lib.keys import SSHKeys
from lib import (
    logger,
    inquirer,
)

from bin import fill_hosts


# For coloring output
from colorama import Fore, Style, init as colorama_init
colorama_init(autoreset=True)


def parse_option() -> object:
    """
    Set arguments list with which script running

    Returns:
        object: The parser object with calling parse_args
    """

    def is_exists_andible_directory(parser: argparse.ArgumentParser, arg):
        if os.path.exists(arg):
            return arg
        else:
            parser.error(f"Directory {arg} is not exists.")

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A tool will create LXD container "
                    "and then running Ansible playbooks onto it.\n"
                    "OpenSSH-server will be deployed by default."
    )
    parser.add_argument(
        '-n', '--name', dest='container_name', metavar='<name>',
        help="Name of created container. Will bonded with container ip addr. "
             "By default will be generated randomly."
    )
    parser.add_argument(
        '--os', dest='template', choices=['ubuntu', 'centos'], default='ubuntu',
        help="Name of LXC OS template. Default: ubuntu"
    )
    parser.add_argument(
        '--release', dest='template_release', metavar='<release>', default='bionic',
        help="Codename of OS release.  Default: ubuntu - bionic; centos - 8"
    )
    parser.add_argument(
        '--ssh-key-private', dest='ssh_priv_key', metavar='<key>',
        type=argparse.FileType('rb'),
        help="Private ssh key if you want use an existing one. "
             "Should be file. Otherwise it will be generated."
    )
    parser.add_argument(
        '--ssh-key-public', dest='ssh_pub_key', metavar='<key>',
        type=argparse.FileType('rb'),
        help="Public ssh key if you want use an existing one. "
             "Should be file. Otherwise it will be generated."
    )
    parser.add_argument(
        '--playbooks-path', dest='playbooks_path', metavar='<path>',
        type=lambda p: is_exists_andible_directory(parser, p),
        help="Path to directory with Ansible playbooks"
        "which needs to run into container."
    )
    parser.add_argument(
        '-v', '--verbose', dest='debug_level', action='store_true',
        help="Verbose output. Print more information about being committed actions. "
             "Will yellow colored."
    )

    return parser.parse_args()


def check_required_program_instance(*program: list) -> None:
    """
    Check that the program is installed and available thru PATH
    If one of programs is not found exit from script

    Args:
        program (list): list of programs names which will to check

    Returns:
        None: Because if required program is not found, script will exiting.
    """

    log = logging.getLogger('lazy_lxd')

    err = False
    for name in program:
        if which(name) is None:
            log.error(f"Could not find {name} executor.")
            err = True
    if err:
        raise SystemExit


def check_recommended_program_instace(*program: list) -> None:
    """
    Check that the program is installed and available thru PATH.
    If programs is not found show warning message.

    Args:
        program (list): list of programs names which will to check

    Returns:
        None: Because if required program is not found, script will show warning only.
    """

    log = logging.getLogger('lazy_lxd')

    err = False
    for name in program:
        if which(name) is None:
            log.warning(f"Could not find {name} executor.")
            err = True

    if err:
        log.warning("It is not necessary but recommended.")


def check_sudo_password(password: str) -> bool:
    """
    Validate password as sudo accessing.
    Running `id -u` with sudo. If password is correct return code will zero.
    Used for validation in PyInquirer question.

    Args:
        password (str): Password received from user.

    Returns:
        bool: True if password valid.
        str: If password not valid return error message.
    """

    sudo_args = "sudo -S id -u"

    sudo_run = subprocess.Popen(sudo_args.split(' '),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)
    sudo_run.communicate(password + '\n')

    if sudo_run.returncode != 0:
        return "Authentication failure"
    return True


def filling_hosts(hostname: str, ip: str, password: str, script_path: str) -> bool:
    """
    Fill the file /etc/hosts with container hostname and it IP address.
    Running separate script `bin/fill-hosts.py` for that.
    Will using super user access and password obtained from user earlier.

    Args:
        hostname (str): Name for 1st script argument.
        ip (str): IP address for 2nd script argument.
        password (str): Password for sudo.
        script_path (str): Path of main script for looking for fill-hosts script.

    Returns:
        bool: True if script executed successfully. Otherwise, False.
    """

    log = logging.getLogger('lazy_lxd')

    script_args = (
        f"sudo {sys.executable} {fill_hosts.__file__} "
        f"{hostname} {ip} /etc/hosts"
    )
    script_run = subprocess.Popen(script_args.split(' '),
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
    out, err = script_run.communicate(password)
    if script_run.returncode != 0:
        log.error(err)
        return False
    else:
        return True


def show_result_info(
    os: str, os_version: str,
    container_name: str, container_host: str,
    private_key: str, is_has_ssh: bool
) -> None:
    """
    Print result of script working.
    Collect available info about container. And show it.
    """

    log = logging.getLogger('lazy_lxd')

    log.info(
        f"{Fore.GREEN}Your container info:{Fore.RESET}\n"
        f"    {Style.BRIGHT}OS:{Style.NORMAL} {os}\n"
        f"    {Style.BRIGHT}OS Version:{Style.NORMAL} {os_version}\n"
        f"    {Style.BRIGHT}Name of container:{Style.NORMAL} {container_name}\n"
        f"    {Style.BRIGHT}Host:{Style.NORMAL} {container_host}"
    )

    if is_has_ssh:
        log.info(
            "\nYou can login into container thru SSH: "
            f"ssh -o IdentitiesOnly=yes -i {private_key} root@{container_host}"
        )


def main():
    """
    The main function.
    """

    arguments = parse_option()

    # Initializing logging subsystem
    logger.init(arguments.debug_level)
    log = logging.getLogger('lazy_lxd')

    script_path = os.path.dirname(os.path.realpath(__file__))

    required_program = ["lxc", "lxd"]
    check_required_program_instance(*required_program)
    recommended_program = ["ansible", "ansible-playbook"]
    check_recommended_program_instace(*recommended_program)

    log.debug("Initializing LXD client.")
    lxd = LXDClient(
        name=arguments.container_name,
        os_template=arguments.template.lower(),
        os_version=arguments.template_release.lower()
    )

    log.debug("Initializing SSH keys.")
    ssh_keys = SSHKeys(
        container_name=lxd.container_name,
        private_key=arguments.ssh_priv_key,
        public_key=arguments.ssh_pub_key
    )

    # if os and release image not exists - download image from internet
    if not lxd.image_exists:
        log.warning(
            f"Image {Style.BRIGHT}"
            f"{lxd.image_os.capitalize()} {lxd.image_version}"
            f"{Style.NORMAL} is not exists in local LXC storage."
        )
        decision = inquirer.confirm("Do you want dowload image:")

        if decision:
            lxd.download_image()
        else:
            raise SystemExit

    # create and run container
    lxd.create_container()
    lxd.start_container()

    if ssh_keys.disable_ssh:
        show_result_info(
            lxd.image_os, lxd.image_version, lxd.container_name, lxd.container_ip,
            None, not ssh_keys.disable_ssh
        )
        return

    lxd.install_openssh()
    lxd.add_ssh_key(ssh_keys.public_key_content)

    # try to fill /etc/hosts with container name and their ip address
    log.info(
        "For easiest access to container, recommended to fill /etc/hosts file.\n"
        "This action needs superuser (sudo) access."
    )
    filled_hosts = inquirer.confirm("Do you want to fill /etc/hosts:")
    if filled_hosts:
        if os.getuid() != 0:
            password = inquirer.password('Root (sudo) password:', check_sudo_password)
            container_has_host_info = filling_hosts(
                lxd.container_name, lxd.container_ip,
                password, script_path
            )
    else:
        container_has_host_info = None

    if arguments.playbooks_path is not None:
        log.debug("Initializing Ansible client.")
        ansible = AnsibleClient(
            playbooks_path=arguments.playbooks_path,
            host=lxd.container_ip,
            ssh_key=ssh_keys.private_key_path
        )

        ansible.start_playbooks()
    else:
        log.warning(
            "Path to directory with Ansible playbooks is empty. "
            "Execution of Ansible client was skipped."
        )

    if container_has_host_info is not None and filled_hosts:
        finally_container_host = lxd.container_name
    else:
        finally_container_host = lxd.container_ip

    show_result_info(
        lxd.image_os, lxd.image_version, lxd.container_name, finally_container_host,
        ssh_keys.private_key_path, not ssh_keys.disable_ssh
    )
