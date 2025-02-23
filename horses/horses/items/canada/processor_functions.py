import re

import arrow
from w3lib.html import remove_tags


def handle_basic(tag):
    return remove_tags(tag).strip()


def convert_to_int(number):
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


def convert_to_float(number):
    if isinstance(number, (int, float)):
        return number

    return float(remove_tags(number).strip())


# auction_result
# ==============
def handle_sales_price(price):
    if isinstance(price, int):
        return price

    price = remove_tags(price)

    return int(price.strip())


def handle_gait(gait):
    return {"p": "pace", "t": "trot"}[remove_tags(gait).strip()]


# horse_info
# ==========
def handle_horse_birthdate(date_string):
    date_string = remove_tags(date_string).strip()

    if "(" in date_string:
        date_string = date_string[
            date_string.find("(") + 1 : date_string.find(")")
        ].strip()

    if len(date_string) == 4 and date_string.isnumeric():
        return f"{date_string}-01-01"

    if re.search(r"\d{4}-\d{2}-\d{2}", date_string):
        return date_string

    if re.search(r"\d{2}-\w{3}-\d{4}", date_string):
        return arrow.get(date_string, "DD-MMM-YYYY").format("YYYY-MM-DD")


def handle_breed(breed):
    if breed in ["standardbred", "thoroughbred", "coldblood"]:
        return breed


def handle_chip(chip):
    chip = remove_tags(chip).strip()

    if "Microchip" in chip:
        chip = chip[chip.find(":") + 2 : chip.find(" ", chip.find(":") + 2)].strip()

    if chip.isnumeric() and len(chip) == 15:
        return chip


def handle_horse_country(name_string):
    name_string = remove_tags(name_string).strip()

    if name_string[-3] == " ":
        state = name_string[-2:]

        if state in [
            "AB",
            "BC",
            "MB",
            "NB",
            "NL",
            "NT",
            "NS",
            "NU",
            "ON",
            "PE",
            "QC",
            "SK",
            "YT",
        ]:
            return "CAN"
        else:
            return "USA"


def handle_gender(gender):
    gender = remove_tags(gender).strip()

    if gender in ["gelding", "horse", "mare"]:
        return gender

    return {
        "g": "gelding",
        "h": "horse",
        "c": "horse",
        "m": "mare",
        "f": "mare",
        "r": "horse",
        "filly": "mare",
        "colt": "horse",
    }[gender]


def handle_horse_name(name_string):
    if "(" in name_string:
        name_string = name_string[: name_string.find("(")]

    return "".join([x for x in name_string if x.isalpha() or x == " "])


# race_info
# =========
def get_distance(conditions):
    conditions = remove_tags(conditions)

    distance = 1

    if "distance" in conditions.lower():
        distance_string = conditions[
            conditions.lower().find("distance") + 8 : conditions.lower().find("miles")
        ].strip()

        full_miles = "0"

        if " " in distance_string:
            full_miles, fraction_string = distance_string.split(" ")
            fraction_split = fraction_string.split("/")

        else:
            fraction_split = distance_string.split("/")

        distance = int(full_miles) + int(fraction_split[0]) / int(fraction_split[1])

    return distance * 1609


def get_gait(conditions):
    conditions = remove_tags(conditions)

    for gait in ["pace", "trot", "both"]:
        if gait in conditions.lower():
            return gait


def is_monte(monte):
    if isinstance(monte, bool):
        return monte

    monte = remove_tags(monte)

    return "saddle" in monte


def get_race_purse(purse):
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse)

    if "--" in purse:
        purse = purse[
            purse.find("purse $") + 5 : purse.find(" ", purse.find("purse $") + 7)
        ]

    if "$" in purse:
        return int(purse.replace("$", "").replace(",", ""))


def get_racenumber(racenumber):
    if isinstance(racenumber, int):
        return racenumber

    racenumber = remove_tags(racenumber).strip()

    if "/racing/" in racenumber:
        racenumber = racenumber[racenumber.find("N") + 1 :]

    if racenumber.isnumeric():
        return int(racenumber)

    return int(racenumber[: racenumber.find(" -- ")].strip())


def get_racetype(conditions):
    return "qualifier" if "Prøveløp" in conditions else "race"


# race_link
# =========
def shorten_race_link(link):
    return link.split("/")[-1]


# race_starter_info
# =================
def handle_person_name(name):
    name = remove_tags(name).strip()

    if "," in name:
        name = " ".join(reversed(name.split(", ")))

    return name


def handle_finish(finish):
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish)

    if "/" in finish:
        finish = finish[: finish.find("/")]

    if "P" in finish:
        finish = finish[finish.find("P") + 1 :]

    return int("".join(x for x in finish if x.isnumeric()))


def handle_starter_purse(purse):
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    return int("".join([x for x in purse if x.isnumeric()]))


def handle_starter_time(time):
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).strip()

    if time != "":
        minutes = "0"

        if ":" in time:
            minutes = time[0]
            seconds = time[2:]
        else:
            seconds = time

        return int(minutes) * 60 + float(seconds)


# raceday_info
# ============
def extract_racetrack_name(meeting_string):
    meeting_string = remove_tags(meeting_string)

    if " - " in meeting_string:
        meeting_string = meeting_string[: meeting_string.find(" - ")]

    if "trackInfo" in meeting_string:
        meeting_string = meeting_string[
            meeting_string.find('("') + 2 : meeting_string.find('","')
        ]

    return meeting_string.strip()


def extract_raceday_date(meeting_string):
    meeting_string = remove_tags(meeting_string).replace("*", "")

    if "-" in meeting_string and "," in meeting_string:
        meeting_string = meeting_string[meeting_string.rfind("-") + 1 :]

        if "(" in meeting_string:
            meeting_string = meeting_string[: meeting_string.find("(")]
        else:
            meeting_string = meeting_string[: meeting_string.find("\n")]

        return arrow.get(meeting_string.strip(), "dddd MMM D, YYYY").format(
            "YYYY-MM-DD"
        )

    if "-" in meeting_string:
        return arrow.get(meeting_string, "DD-MMM-YYYY").format("YYYY-MM-DD")


# raceday_link
# ============
def shorten_raceday_link(link):
    link = remove_tags(link).strip()

    if "#" in link:
        link = link[: link.find("#")]

    return link.split("/")[-1]


# registration
# ============
def shorten_horse_link(link):
    if link.isnumeric():
        return link

    if "id=" in link:
        link = link[link.find("id=") + 3 :]

    if "&" in link:
        link = link[: link.find("&")]

    return link


# def raceday_date_from_link(link):
#     return link.split('/')[-2]
#
#
# def racetrack_code_from_link(link):
#     return link.split('/')[-1]
#
#
# def remove_meeting(racetrack):
#     if racetrack[1].isdigit() and racetrack[0] == 'R':
#         return ' '.join(racetrack.split(' ')[1:])
#
#     return racetrack
#
#
# def remove_racenumber(racename):
#     if racename[1].isdigit() and racename[0] == 'C':
#         return ' '.join(racename.split(' ')[1:])
#
#     return racename
#
#
def get_startmethod(conditions):
    return "mobile" if "autostart" in conditions.lower() else "standing"


def handle_horse_purse(purse_string):
    return purse_string.replace("$", "").replace(",", "")


def strip_comma(price):
    return price.replace(",", "")


# def handle_horse_name(name_string):
#     if '(' in name_string:
#         name_string = name_string[:name_string.find('(')]
#
#     return name_string
#
#
# def handle_starter_distance(dist):
#     return ''.join([x for x in dist if x.isdigit()])
#
#
# def handle_starter_finish(res: str):
#     if res.isnumeric():
#         return res
#
#
# def did_start(res: str):
#     return 'NP' not in res.upper()
#
#
def shorten_conditions(conditions_string):
    conditions_parts = [
        x for x in conditions_string.split("\n\n") if "kr." in x or "Prøveløp" in x
    ]

    if len(conditions_parts) == 1:
        return conditions_parts[0]


def handle_starter_finish(finish):
    if isinstance(finish, str):
        return int(finish) if finish.isnumeric() else 0

    return finish


def handle_comma(num):
    return num.replace(",", ".")

