import os
import logging
import json

from .playbook import (
    choose_playbooks,
    is_exists_playbooks,
    redefine_playbooks_path
)
from .execute import run_ansible_playbook


class AnsibleClient(object):
    """
    Client for conversation with Ansible, and running it playbooks to container.

    Args:
        playbooks_path (str): Path to directory with Ansible playbooks
                              which needs to run into container.
        container_host (str): Host or IP address of container
                              in which would be running playbooks.
        ssh_key (str): Path to SSH private key
                       which needs to using to connect by Ansible.
    """

    def __init__(
        self,
        playbooks_path: str,
        host: str,
        ssh_key: str
    ):
        # functions
        # executing ansible playbooks
        self.__run_playbook = run_ansible_playbook

        self._log = logging.getLogger('lazy_lxd')

        self.playbooks_path = playbooks_path
        self.container_host = host
        self.playbooks = self.__get_playbooks()

        self.ssh_key = ssh_key

    def __get_playbooks(self):
        """
        Scan playbooks directory, get filenames and
        give the user choose playbooks which he want to play.
        """

        if not is_exists_playbooks(self.playbooks_path):
            self._log.error(
                f"Directory {self.playbooks_path} doesn't contains no one y(a)ml file."
            )
            while True:
                try:
                    self.playbooks_path = redefine_playbooks_path()
                    self._log.debug(
                        "Recieved new path to directory"
                        f"with Ansible playbooks {self.playbooks_path}"
                    )
                    return self.__get_playbooks()
                except FileNotFoundError as e:
                    self._log.error(e)

        playbooks = choose_playbooks(self.playbooks_path)

        if len(playbooks) == 0:
            self._log.warning("You didn't select Ansible playbooks to run.")
            return self.__get_playbooks()
        else:
            return playbooks

    def start_playbooks(self):
        """
        Running all ansible playbooks which user is choosed.
        Exit code and stdout are parsing for looking for errors.
        """

        for p in self.playbooks:
            self._log.debug(f"Preparing to execute Ansible playbook {p}")
            status, out, err, command = self.__run_playbook(self, p)

            if status > 0:
                self._log.error(f"Was occurred while running playbook {p}: {err}")
                self._log.warning(f"Try execute command yourself: {command}")

            else:
                if out['stats'][self.container_host]['failures'] > 0:
                    self._log.warning(
                        f"Something was failing while executing playbook {p}"
                    )
                    self._log.warning(f"Try execute command yourself: {command}")
                else:
                    self._log.debug(f"Playbook {p} is completed.")
