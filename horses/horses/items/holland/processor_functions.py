import re

import arrow
from w3lib.html import remove_tags


def handle_basic(tag: str) -> str:
    return remove_tags(tag).strip()


def convert_to_int(number: str | int) -> int:
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


# horse_info
# ==========
def handle_date(date_string: str) -> str:
    date_string = remove_tags(date_string).strip()

    if "-" in date_string:
        if date_string[3].isnumeric():
            return arrow.get(date_string, "DD-MM-YY").format("YYYY-MM-DD")

        if date_string[3].isalpha():
            return arrow.get(
                date_string,
                "D-MMM-YYYY" if len(date_string) in [10, 11] else "D-MMM-YY",
                locale="nl-nl",
            ).format("YYYY-MM-DD")

    return arrow.get(date_string, "D MMMM YYYY", locale="nl-nl").format("YYYY-MM-DD")


def handle_country(country: str) -> str | None:
    country = remove_tags(country).strip()

    if "(" in country:
        country = country[country.find("(") + 1 : country.find(")")]

    if len(country) < 3:
        return country

    if country[-1].isdigit():
        return "".join(x for x in country if not x.isdigit())

    return None


def handle_gender(gender: str) -> str:
    gender = remove_tags(gender).strip()

    if gender in ["horse", "gelding", "mare"]:
        return gender

    if "(" in gender:
        gender = gender[gender.find("(") + 1 : gender.find(")")]

    return {
        "Ruin": "gelding",
        "Merrie": "mare",
        "Hengst": "horse",
        "R": "gelding",
        "M": "mare",
        "H": "horse",
    }[gender]


def handle_name(name: str) -> str:
    name = remove_tags(name)

    if "(" in name:
        return name[: name.find("(")]

    return name.strip().upper()


# race_info
# =========
def handle_distance(distance: str | int) -> int:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance)

    if "-" in distance:
        distance = distance.split("-")[1]

    return int(distance) if distance.strip().isnumeric() else 0


def handle_purse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    purse = "".join([x for x in purse.replace(",00", "") if x.isnumeric()])

    return int(purse) if purse.isnumeric() else 0


def handle_racenumber(number: str | int) -> int | None:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    if number.isdigit():
        return int(number)

    return None


def handle_racetype(racetype: str) -> str:
    racetype = remove_tags(racetype)

    return "qualifier" if racetype == "KW" else "race"


def handle_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod)

    return "mobile" if "autostart" in startmethod.lower() else "standing"


# race_starter_info
# =================
def is_disqualified(disqualified: str | bool) -> bool:
    if isinstance(disqualified, bool):
        return disqualified

    return "A" in remove_tags(disqualified)


def handle_driver(driver: str) -> str:
    driver = remove_tags(driver).strip()

    return re.sub(r"\s{2,}", r" ", driver)


def handle_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).strip()

    return int(finish) if finish.isdigit() else 0


def handle_place_odds(odds: str | int | float) -> int | float:
    if isinstance(odds, (int, float)):
        return odds

    odds = remove_tags(odds)

    return int(odds) / 10


def handle_time(time: str | int | float) -> int | float | None:
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).strip()

    if ":" in time:
        minutes = int(time[: time.find(":")])
        seconds = float(time[time.find(":") + 1 :].replace(",", "."))

        return minutes * 60 + seconds

    return None


def handle_startnumber(number: str | int) -> int:
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


def handle_odds(odds: str | int | float) -> int | float:
    if isinstance(odds, (int, float)):
        return odds

    odds = remove_tags(odds).strip()

    if odds == "":
        return 0

    return float(odds.replace(",", "."))
