import os
from typing import BinaryIO


def search_public_key(priv_key: str) -> BinaryIO:
    """
    Looking for public key. Usually file name have suffix .pub.

    Args:
        priv_key (str): Path to private key.

    Returns:
        BinaryIO: Public part of SSH public as opened binary file.
    """

    priv_key_path = priv_key
    pub_key_path = f'{priv_key_path}-cert.pub'
    if os.path.exists(pub_key_path):
        return open(pub_key_path, 'rb')
    else:
        raise FileNotFoundError(pub_key_path)
