def create(name: str) -> bool:
    """
    Generate SSH key pair and save their into $HOME/.ssh

    Args:
        name (str): Name of ssh keys.
                    Future naming will <name> for private, and <name>.pub for public key

    Returns:
        bool: Status of saving keys operation, True if successful. Otherwise, False.
    """

    keys = _generate()
    return _save(name, keys)


def _generate() -> tuple:
    """
    Generate SSH key pair
    Used RSA with length 2048 bit for a more secure

    Returns:
        tuple: Private and public SSH key pair as bytes strings
    """

    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    return (private_key, public_key)


def _save(name: str, keys: tuple) -> tuple:
    """
    Save obtained keys into $HOME/.ssh directory

    Args:
        name (str): Future name of key pair files.
                    Naming will be <name> for private,
                    and <name>.pub for public parts of key.

    Returns:
        tuple: Private and public SSH key pair as BinaryIO.
    """

    from os import path, environ, chmod
    import logging

    log = logging.getLogger('lazy_lxd')

    home_env = environ['HOME']
    ssh_dir = path.join(home_env, '.ssh')
    log.debug(f"Saving keys into {ssh_dir}")

    private_key = path.join(ssh_dir, name)
    public_key = path.join(ssh_dir, name + '-cert.pub')

    try:
        with open(private_key, 'wb') as pf:
            pf.write(keys[0])
        chmod(private_key, 0o600)
        with open(public_key, 'wb') as pb:
            pb.write(keys[1])
        return (open(private_key, 'rb'), open(public_key, 'rb'))
    except (PermissionError, FileNotFoundError) as e:
        log.error(e)
        raise SystemExit(1)
