import logging
from typing import BinaryIO

import pylxd

from .container import (
    set_name,
    create,
    delete,
    run,
    restart,
    get_network_address
)
from .image import (
    exists,
    download,
    get_fingerprint
)
from .execute import (
    run_command
)


class LXDClient():
    """
    Instance of pylxd Client with methods to interact with it.
    Contain additional info about container and it image.

    Args:
        name (str): Name of future LXD container.
        os_template (str): Name of OS for image from where will create container.
        os_version (str): Version of requested image. Could be as codename and version.
    """

    def __init__(
        self,
        name: str,
        os_template: str, os_version: str,
    ):
        # functions
        # container
        self.__set_container_name = set_name
        self._create_container = create
        # image
        self.__is_exists_image = exists
        self._download_image = download
        self._get_image_fingerprint = get_fingerprint

        # variables and constants
        self._client = pylxd.Client()
        self._log = logging.getLogger('lazy_lxd')

        self.__container = None
        self.container_name = self.__set_container_name(self, name)
        self.container_ip = None
        self.container_is_running = False

        self.image_os = os_template
        self.image_version = self.__get_os_codename_version(os_version)
        self.image_exists = self.__is_exists_image(self)
        self.image_fingerprint = None

    def download_image(self) -> None:
        """
        Download LXD image from linuxcontainers.org to local storage.
        """

        try:
            self._log.debug(
                f"Downloading image {self.image_os}:{self.image_version} from "
                "linuxcontainers.org."
            )
            self._download_image(self)
        except pylxd.exceptions.LXDAPIException as e:
            self._log.error(str(e))
            raise SystemExit

    def create_container(self) -> None:
        """
        Create LXD empty container from the existing image using it fingerprint.
        At first, looking for image fingerprint.
        If found more than one requested image, offer choose from list.
        List contains images which fits by requested criteria.
        """

        self.image_fingerprint = self._get_image_fingerprint(self)
        self._log.debug(
            f"Got image {self.image_os}:{self.image_version} "
            f"fingerprint: {self.image_fingerprint}"
        )

        try:
            self._log.debug(
                f"Creating container {self.container_name} "
                f"from image {self.image_os}:{self.image_version}"
            )
            self.__container = self._create_container(self)
        except pylxd.exceptions.LXDAPIException as e:
            self._log.error(str(e))
            raise SystemExit

    def start_container(self):
        """
        Start LXD container.
        And waiting until it network will becomes available.
        """

        try:
            self._log.debug(f"Starting container {self.container_name}")
            run(self.__container)
            self.container_is_running = True

        except TimeoutError as e:
            self._log.error(str(e))
            self.__delete_container()
            raise SystemExit

        except pylxd.exceptions.LXDAPIException as e:
            try:
                if not self.container_is_running:
                    self._log.debug(f"Restarting container. Occurred exception {e}.")
                    restart(self.__container)
            except pylxd.exceptions.LXDAPIException as e:
                self._log.error(str(e))
                self.__delete_container()
                raise SystemExit

        else:
            self.container_ip = get_network_address(self.__container)
            self._log.debug(
                f"Container {self.container_name} has IP address {self.container_ip}"
            )

    def install_openssh(self):
        """
        Installing OpenSSH server into container.
        Running install command inside container.
        """

        if self.image_os == 'ubuntu':
            install_command = 'apt-get -y install openssh-server'
        elif self.image_os == 'centos':
            install_command = 'yum -y install openssh-server'

        try:
            out, err = run_command(self.__container, install_command)
            if self.image_os == 'centos':
                install_command += '; service sshd start'
                out, err = run_command(self.__container, 'service sshd start')
        except (RuntimeError, ValueError) as e:
            self._log.error(
                "Occurred error while installing openssh server into container. "
                f"Got exit code {e} while performing "
                f"'{install_command}' inside container."
            )
            raise SystemExit(1)
        else:
            if err != '':
                self._log.debug(f"Got error message: {err.strip()}")

    def add_ssh_key(self, key: BinaryIO):
        """
        Copy public SSH key to container.
        Prepare for it, creating ~/.ssh directory.
        After copying key, change mode on Authorized_keys to 600.

        Args:
            key (BinaryIO): Public part of SSH key.
        """

        try:
            run_command(self.__container, 'test -d /root/.ssh')
        except RuntimeError:
            try:
                command = 'mkdir /root/.ssh; chmod 700 /root/.ssh'
                out, err = run_command(self.__container, 'mkdir /root/.ssh')
                out, err = run_command(self.__container, 'chmod 700 /root/.ssh')
            except (RuntimeError, ValueError) as e:
                self._log.error(
                    "Occurred error while preparing directories for SSH. "
                    f"Got exit code {e} while performing '{command}' inside container."
                )
                raise SystemExit(1)
            else:
                if err != '':
                    self._log.debug(f"Got error message: {err.strip()}")

        try:
            self.__container.files.put('/root/.ssh/authorized_keys', key)
            command = 'chmod 600 /root/.ssh/authorized_keys'
            out, err = run_command(self.__container, command)
        except (RuntimeError, ValueError) as e:
            self._log.error(
                "Occurred error while write SSH public key to Authorized keys. "
                f"Got exit code {e} while performing '{command}' inside container."
            )
            raise SystemExit(1)

    def __delete_container(self):
        """
        Delete empty LXD container.
        Use only for cleaning before exit from script after catching an error.
        """

        try:
            self._log.debug(
                "Delete empty container because have errors while starting it."
            )
            delete(self.__container)
            self.container_is_running = False

        except pylxd.exceptions.LXDAPIException as e:
            self._log.error(str(e))
            self._log.error(
                f"Please delete container {self.container_name} by yourself."
            )
            raise SystemExit

    def __get_os_codename_version(self, version: str) -> str:
        """
        Get correctly version for OS.
        No matter what was passed into arguments. Codename or version.
        Convert Ubuntu os codename to version as number and vice versa.
        If OS is centos and version is not setted, return default version.
        For other OS is useless. Returns values from args if is setted.

        Args:
            version (str): OS codename or version number

        Returns:
            tuple: OS version
        """

        versions = {
            "14.04": "trusty",
            "16.04": "xenial",
            "18.04": "bionic",
            "19.10": "eoan",
            "20.04": "focal"
        }

        # TODO: что-то здесь не так. Надо упростить. Оставить только один default.
        # Все для ubuntu. Проверить что linuxcontainers принимает и номер и codename.

        if self.image_os != 'ubuntu' and version != 'bionic':
            return version
        elif self.image_os != 'ubuntu':
            if self.image_os == 'centos':
                return str(8)  # default centos version
            # if os != Ubuntu and os version == bionic it shouldn't be
            else:
                self._log.warning(
                    f"Please enter to version for requested OS {self.image_os}"
                )
                raise SystemExit

        version_num = None
        for key, value in versions.items():
            if key == version or value == version:
                version_num = value
                break
        return version_num if version_num is not None else version
