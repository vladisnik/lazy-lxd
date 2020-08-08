import os

from lib import inquirer


def choose_playbooks(path: str) -> list:
    """
    Scan playbooks directory, get file names and
    give the user choose playbooks which he want to play.

    Args:
        path (str): Path to directory with Ansible playbooks.

    Returns:
        list: Playbooks with file extension that have been chosen by user.
    """

    playbooks = list()
    files = os.listdir(path)

    for file in files:
        if _check_extension(file):
            playbooks.append(os.path.basename(file))

    chosen_playbooks = inquirer.checkbox(
        list(map(lambda file: os.path.splitext(file)[0], playbooks)),
        "Choose playbooks which you want to run into container"
    )

    return list(map(lambda i: playbooks[i], chosen_playbooks))


def is_exists_playbooks(path: str) -> bool:
    """
    Check that directory with playbooks contains at least one playbook as y(a)ml file.

    Args:
        path (str): Path to directory with Ansible playbooks.

    Return:
        bool: True if have playbooks in directory. Otherwise, False.
    """

    files = os.listdir(path)
    for file in files:
        if _check_extension(file):
            return True

    return False


def redefine_playbooks_path() -> str:
    """
    Get new path to directory with Ansible playbooks.

    Returns:
        str: Path to directory with Ansible playbooks.
    """

    path = inquirer.input_text("Type new path to directory with Ansible playbooks")
    if os.path.exists(path):
        return path
    else:
        raise FileNotFoundError(f"Directory {path} is not exists.")


def _check_extension(file) -> bool:
    """
    Check that file extension is equal yaml or yml.

    Args:
        file (str): Name or path to of file.

    Returns:
        bool: True if file extension is equal of yaml or yml. Otherwise False.
    """

    extension = os.path.splitext(file)[1]
    return True if extension == '.yaml' or extension == '.yml' else False
