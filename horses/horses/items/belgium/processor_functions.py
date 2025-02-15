from datetime import datetime

import arrow
from w3lib.html import remove_tags


def handle_basic(value: str) -> str:
    value = remove_tags(value)

    return value.strip()


# horse_info
# ==========
def handle_gender(gender: str) -> str | None:
    gender = remove_tags(gender).strip().lower()

    if gender == "rien":
        return None

    if "," in gender:
        gender = gender.replace(",", "").strip()

    if gender in ["gelding", "horse", "mare"]:
        return gender

    return {"standaard": "horse", "merrie": "mare", "ruin": "gelding"}[gender]


def handle_birthdate(date_string: str) -> str | None:
    date_string = remove_tags(date_string).strip()

    if len(date_string) == 4 and date_string.isdigit():
        return f"{date_string}-01-01"

    if len(date_string) == 10:
        if date_string[4] == "-":
            return date_string

        return "-".join(reversed(date_string.split("-")))

    if len(date_string) == 8:
        return arrow.get(date_string, "DD-MM-YY").format("YYYY-MM-DD")

    return None


def handle_name(name: str) -> str:
    name = remove_tags(name)

    if "[" in name:
        name = name[: name.find("[")]

    return name.strip().upper()


# race_info
# =========
def handle_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod)

    return "mobile" if "autostart" in startmethod.lower() else "standing"


def is_monte(monte: str | bool) -> bool:
    if isinstance(monte, bool):
        return monte

    monte = remove_tags(monte)

    return "monté" in monte.lower()


def handle_racepurse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse)

    return int(purse[purse.find("(P)") + 3 : purse.find("€")])


def handle_racetype(name: str) -> str:
    name = remove_tags(name)

    return "qualifier" if "kwalificatie" in name.lower() else "race"


def handle_racenumber(number: str | int) -> int | None:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    if number.isnumeric():
        return int(number)

    return None


def remove_time(name_string: str) -> str:
    name_string = remove_tags(name_string)

    if name_string[0].isnumeric():
        name_string = name_string[name_string.find("-") + 1 :]

    return name_string.strip()


def handle_distance(distance: str | int) -> int:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance)

    if "-" in distance:
        distance = distance.split("-")[1]

    return int(distance.replace("m", "").strip())


# race_link
# =========
def handle_racelink(link: str) -> str:
    return link[link.find("#") + 1 :]


# race_starter_info
# =================
def did_start(place_string: str) -> bool:
    return "np" not in place_string.lower()


def was_disqualified(finished: str | bool) -> bool:
    if isinstance(finished, bool):
        return finished

    finished = remove_tags(finished)

    return "d" in finished.lower()


def handle_horsepurse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse)

    purse = purse.replace("€", "").strip()

    return int(purse) if purse != "" else 0


def handle_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).strip()

    return int(finish) if finish.isnumeric() else 0


def handle_startnumber(number: str | int) -> int:
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


# race_time
# =========
def handle_racetime(time: str | int | float) -> int | float | None:
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).strip()

    time_splits = time.split(":")

    if len(time_splits) == 3:
        minutes, sec, tenths = time_splits

        return int(minutes) * 60 + int(sec) + int(tenths) / 10

    return None


# raceday_info
# ============
def handle_raceday_date(date_string: str) -> str:
    date_string = remove_tags(date_string).strip()

    return arrow.get(date_string, "DD-MM-YYYY").format("YYYY-MM-DD")


# raceday_link
# ============
def handle_racedaylink(link: str) -> str:
    return link[link.find("/", 2) + 1 : link.find("#")]


# registration
# ============
def handle_registration(name_string: str) -> str | None:
    name_string = remove_tags(name_string).strip()

    if "[" in name_string:
        return name_string[name_string.find("[") + 1 : name_string.find("]")]

    if len(name_string) == 7 and name_string[-1].isnumeric():
        return name_string

    return None


def handle_horselink(link: str) -> str | None:
    if "/" in link:
        return link.split("/")[-1]

    if link.isnumeric():
        return link

    return None


# result_summary
# ==============
