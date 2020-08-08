from PyInquirer import prompt
from .confirm import confirm


def input_text(msg: str = "Type something") -> str:
    """
    Ask user to enter text in response to a request input answer

    Args:
        msg (str): Message which display to user. This is request for input text usually.

    Returns:
        str: Text which user entered
    """

    question = [
        {
            "type": "input",
            "name": "input",
            "message": msg
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
            return input_text(msg)
