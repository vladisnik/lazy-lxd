def convert_to_list_with_index(items: list) -> list:
    """
    Prepare simple list to inquirer list.
    Convert to dicts list, with 2 keys: index and value from original list

    Args:
        items (list): Original items list which needs to convert

    Return:
        list: List of dicts with index key and item
    """

    return [{'value': index, 'name': item} for index, item in enumerate(items)]
