from PyInquirer import prompt
from .confirm import confirm

from typing import Callable


def password(msg: str = "Your password", validate: Callable[..., bool] = None) -> str:
    """
    Ask user to enter password. It will be hide on the screen by *

    Args:
        msg (str): Message which display to user. This is request for input text usually.
        validate (callable): Function which will validate entered password.
                             Should return True if successfull, or str if not.

    Returns:
        str: Password which user entered
    """

    question = [
        {
            'type': 'password',
            'name': 'input',
            'message': msg,
            'validate': validate
        }
    ]
    try:
        answer = prompt(question)
        return answer['input']
    except KeyError:
        exit = confirm(msg="Do you want cancel script")
        if exit:
            raise SystemExit
        else:
            return password(msg, validate)
