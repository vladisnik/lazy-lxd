from PyInquirer import prompt
from .confirm import confirm
from .lists import convert_to_list_with_index


def choose(choices: list, msg: str = "What do you choose") -> int:
    """
    Ask user to choose variant from choices list.


    Args:
        msg (str): Message which display to user. This is question usually.
        choices (list): List with items among which user will choosing.

    Returns:
        int: Index in choices list which user choosed
    """

    question = [
        {
            'type': 'list',
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
            return choose(choices, msg)
