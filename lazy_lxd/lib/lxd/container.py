from coolname import generate_slug
from colorama import Style
from halo import Halo
from lib import inquirer


def set_name(self, name: str) -> str:
    """
    Set container name from arguments.
    If name not setted. Generate random name.
    If container exists suggest user promt new name of generate random name

    Args:
        name (str): Desired name of container from arguments.

    Returns:
        str: Name of container.
    """

    # generate random name
    if name is None or name == '':
        return generate_slug(2)

    if not self._client.containers.exists(name):
        return name
    else:
        self._log.warning(
            f"Container {Style.BRIGHT}{name}{Style.NORMAL} exists already."
        )
        self._log.info(
            "Please prompt new container name.\n"
            "If you leave blank input form, will be generate random name."
        )
        new_name = inquirer.input_text("New container name:")

        return set_name(self, new_name)


def create(self) -> object:
    """
    Create empty container with specific os/release.

    Returns:
        object: pylxd container object
    """

    config = {
        'name': self.container_name,
        'source': {
            'type': 'image',
            'fingerprint': self.image_fingerprint
        },
    }
    try:
        with Halo(text="Create container...", spinner="dots12", color="blue"):
            container = self._client.containers.create(config, wait=True)
    except Exception as e:
        raise e

    return container


def run(container: object) -> bool:
    """
    Start LXD container. Wait until network becomes available.

    Args:
        container (object): pylxd container object

    Returns:
        bool: Return True if container started. False if something went wrong
    """

    import time

    # 30 seconds timeout
    timeout = time.time() + 30
    try:
        with Halo(text="Start container...", spinner="dots12", color="blue"):
            container.start(wait=True)
            while True:
                address = get_network_address(container)
                if address is not None:
                    break
                if time.time() > timeout:
                    raise TimeoutError("The container doesn't receive network too long")
                time.sleep(1)
            return True
    except Exception as e:
        raise e
        return False


def stop(container: object) -> bool:
    """
    Stop LXD container

    Args:
        container (object): pylxd container object

    Returns:
        bool: Return True if container stopped. False if something went wrong
    """

    try:
        with Halo(text="Stop container...", spinner="dots12", color="blue"):
            container.stop(wait=True)
            return True
    except Exception as e:
        raise e
        return False


def restart(container: object) -> bool:
    """
    Restart LXD container.
    Do it with stop and start function to guarantee full start with network.

    Args:
        container (object): pylxd container object.

    Returns:
        bool: Return True if container restarted. False if something went wrong.
    """

    try:
        stop(container)
        run(container)
        return True
    except Exception as e:
        raise e
        return False


def delete(container: object) -> bool:
    """
    Delete LXD container.

    Args:
        container (object): pylxd container object.

    Returns:
        bool: Return True if container deleted successfully. Otherwise, False.
    """

    try:
        stop(container)
        with Halo(text="Delete container...", spinner="dots12", color="blue"):
            container.delete(wait=True)
            return True
    except Exception as e:
        raise e
        return False


def get_network_address(container: object) -> str:
    """
    Get container state and find external network address

    Args:
        container (object): pylxd container object

    Returns:
        str: Container network address
    """

    try:
        state = container.state()
        for network, interface in state.network.items():
            if network == 'eth0':
                for ipv in interface['addresses']:
                    if ipv['family'] == 'inet':
                        return ipv['address']
    except AttributeError:
        if state.status == 'Stopped':
            run(container)
            get_network_address(container)
