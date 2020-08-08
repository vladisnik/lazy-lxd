from PyInquirer import prompt
from .confirm import confirm
from .lists import convert_to_list_with_index


def checkbox(choices: list, msg: str = "What you will choose") -> list:
    """
    Ask user to choose of many variant from list of options.

    Args:
        choices (list): List with items among which user will choosing.
        msg (str): Message which display to user. This is question usually.

    Returns:
        list: Options that have been chosen by user.
    """

    question = [
        {
            'type': 'checkbox',
            'name': 'selected',
            'message': msg,
            'choices': convert_to_list_with_index(choices)
        }
    ]
    try:
        answer = prompt(question)
        return answer['selected']
    except KeyError:
        exit = confirm(msg="Do you want cancel script")
        if exit:
            raise SystemExit
        else:
            return checkbox(choices, msg)
