import logging
from typing import BinaryIO

from lib import inquirer

from .search import search_public_key
from .validate import valid
from .create import create


class SSHKeys(object):
    """
    Place for storing SSH keys.
    It provides tools for validating and creating keys.

    Args:
        private_key (BinaryIO): Private part of SSH key as opened file with bytes mode.
        public_key (BinaryIO): Public part of SSH key as opened file with bytes mode.
        container_name (str): Name of container which is beaning creating.
                              Needs as name to creating SSH keys if it needed.
    """

    def __init__(
        self,
        container_name: str,
        private_key: BinaryIO = None,
        public_key: BinaryIO = None,
    ):
        self._log = logging.getLogger('lazy_lxd')

        self.private_key = None
        self.public_key = None

        self.container_name = container_name

        self.private_key_path = None
        self.public_key_path = None

        self.disable_ssh = False
        self._keys_is_valid = False
        self._create_keys = False

        self.__initialize_keys(private_key, public_key)

    def __initialize_keys(self, private_key: BinaryIO, public_key: BinaryIO):
        """
        Processing keys obtained from class arguments.
        Checking their exists, get content and path. Saving it into class properties.
        Validating keys correctness.
        Creating new if keys obtained from arguments is not exists.

        Args:
            private_key (BinaryIO): Private part of SSH key
                                    as opened file with bytes mode.
            public_key (BinaryIO): Public part of SSH key
                                   as opened file with bytes mode.
        """

        if private_key is not None and public_key is None:
            try:
                self._log.debug(
                    f"Looking for ssh public key by path {private_key.name}-cert.pub."
                )
                public_key = search_public_key(private_key.name)
                self._log.debug(f"Found public part of SSH key {public_key.name}")
            except FileNotFoundError as e:
                self._log.error(f"Public part of SSH key is not found by path {e}")

        if private_key is not None and public_key is not None:
            private_key_content = private_key.read()
            public_key_content = public_key.read()
            self._keys_is_valid = valid(private_key_content, public_key_content)
            if not self._keys_is_valid:
                self._log.error("Keys pair has invalid signature.")

        if not self._keys_is_valid:
            self._create_keys = inquirer.confirm(
                "Create new SSH key pair\n"
                "  Will be named by name of container."
            )
            if not self._create_keys:
                self.disable_ssh = True
                self._log.warning(
                    "SSH was disabled couse haven't keys.\n"
                    "Will be create container only."
                )
                return
            else:
                self._log.debug(f"Creating SSH keys by name {self.container_name}")
                private_key, public_key = create(self.container_name)

        # prevent EOF pointer
        private_key.seek(0)
        public_key.seek(0)

        self.private_key_content = private_key.read()
        self.public_key_content = public_key.read()
        self.private_key_path = private_key.name
        self.public_key_path = public_key.name
