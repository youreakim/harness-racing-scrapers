from w3lib.html import remove_tags


def handle_basic(tag):
    return remove_tags(tag).strip()


def convert_to_int(number):
    if isinstance(number, (int, float)):
        return int(number)

    if number.strip() != '':
        return int(remove_tags(number).strip())


def convert_to_float(number):
    if isinstance(number, (int, float)):
        return number

    if number.strip() != '':
        return float(remove_tags(number).replace(',', '.').strip())
