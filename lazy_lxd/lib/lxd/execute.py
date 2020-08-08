from halo import Halo


def run_command(container: object, cmd: str) -> tuple:
    """
    Run command inside in container.

    Args:
        cmd (list): Command which needs to execute in container.
        container (object): pylxd container object

    Returns:
        tuple: Standart and error command output.
    """

    with Halo(
        text="Executing a job inside container...",
        spinner="dots12", color="blue"
    ):
        code, out, err = container.execute(cmd.split(' '))
        if code != 0:
            raise RuntimeError(code)
        return (out, err)
