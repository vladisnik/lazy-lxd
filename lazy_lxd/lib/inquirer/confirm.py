from PyInquirer import prompt


def confirm(msg: str = "Do you want it:", default: bool = True) -> bool:
    """
    Ask user to confirm something

    Args:
        msg (str): Message which display to user. This is question usually.
        default (bool): Decision by default. True agreed, False vice versa.

    Returns:
        bool: True user is agreed. False if not.
    """

    question = [
        {
            'type': 'confirm',
            'name': 'confirm',
            'message': msg,
            'default': default
        }
    ]
    try:
        answer = prompt(question)
        return answer['confirm']
    except KeyError:
        exit = confirm(msg="Do you want cancel script")
        if exit:
            raise SystemExit
        else:
            return confirm(msg, default)
