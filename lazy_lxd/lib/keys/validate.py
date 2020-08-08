import logging
import binascii

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import exceptions as crypt_exceptions


def valid(private: bytes, public: bytes) -> bool:
    """
    Full validating ssh key.
    They should be presented on the specified paths, and valid pair.

    # TODO: add private key password support

    Args:
        private (bytes): Private part of SSH key file content as byte string.
        public (bytes): Public part of SSH key file content as byte string.

    Returns:
        bool: True if keys was passed validation. Otherwise False.
    """

    log = logging.getLogger('lazy_lxd')

    try:
        try:
            private_key = serialization.load_pem_private_key(
                private,
                password=None,
                backend=default_backend()
            )
        except binascii.Error as e:
            log.error(f"Invalid private part of SSH key: {e}")
            return False

        try:
            public_key = serialization.load_ssh_public_key(
                public,
                backend=default_backend()
            )
        except binascii.Error as e:
            log.error(f"Invalid public part of SSH key: {e}")
            return False

        test_message = b'testing keys'
        sha_padding = padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        )

        signature = private_key.sign(
            test_message,
            sha_padding,
            hashes.SHA256()
        )
        public_key.verify(
            signature,
            test_message,
            sha_padding,
            hashes.SHA256()
        )

    except crypt_exceptions.InvalidSignature:
        return False
    except crypt_exceptions.UnsupportedAlgorithm as e:
        log.warning(e)
        return False
    except TypeError:
        log.warning("Private key with password is not supported yet.")
        return False
    else:
        return True
