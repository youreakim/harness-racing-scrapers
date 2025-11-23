from datetime import datetime

import arrow
from w3lib.html import remove_tags


def handle_basic(tag: str) -> str:
    return remove_tags(tag).strip()


def convert_to_int(number: str | int) -> int:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    return int(number) if number != "" else 0


# horse_info
# ==========
def handle_birthdate(date: str) -> str | None:
    date = remove_tags(date).strip()

    if " " in date:
        date = date[: date.find(" ")]

    if date.isdigit() and len(date) < 3:
        current_year = datetime.today().year
        return f"{current_year - int(date)}-01-01"

    if date.isdigit() and len(date) == 4:
        return f"{date}-01-01"

    if "/" in date:
        date_splits = ["".join([z for z in x if z.isdigit()]) for x in date.split("/")]
        return "-".join(reversed(date_splits))

    if "-" in date:
        return date


def handle_gender(gender: str) -> str | None:
    gender = remove_tags(gender).strip().lower()

    if gender in ["horse", "mare", "gelding"]:
        return gender

    if gender == "":
        return None

    return {
        "macho": "horse",
        "caballo castrado": "gelding",
        "macho castrado": "gelding",
        "castrado": "gelding",
        "hembra": "mare",
        "m": "horse",
        "h": "mare",
        "c": "gelding",
    }[gender]


def handle_country(name: str) -> str:
    name = remove_tags(name).strip()

    if "(" in name:
        return name[name.find("(") + 1 : name.find(")")]

    return "ES"


def handle_name(name: str) -> str:
    name = remove_tags(name)

    if "(" in name:
        name = name[: name.find("(")]

    return name.strip().upper()


# race_info
# =========
def handle_distance(distance: str | int) -> int:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance)

    if "Distancia" in distance:
        distance = distance[distance.find("Distancia") + len("Distancia") :]

    return int(distance.replace(".", "").replace("m", ""))


def handle_purse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).replace("€", "").replace(".", "").strip()

    if "," in purse:
        purse = purse[: purse.find(",")]

    return int(purse) if purse.isdigit() else 0


def get_racenumber(number: str | int) -> int | None:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    if "-" in number:
        number = number[: number.find("-")].strip()

    if number.isdigit():
        return int(number)


def handle_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod).lower()

    return "mobile" if "autostart" in startmethod else "standing"


# race_link
# =========
def get_race_id(link: str) -> str:
    if "idCarrera=" in link:
        link = link[link.find("idCarrera=") + 10:]

    if "&" in link:
        link = link[:link.find("&")]

    return link


# race_starter_info
# =================
def is_disqualified(disqualified: str | bool) -> bool:
    if isinstance(disqualified, bool):
        return disqualified

    return "d" in remove_tags(disqualified).lower()


def handle_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).strip()

    return int(finish.replace(".", "")) if "." in finish else 0


def handle_racetime(time: str | int | float) -> int | float:
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).replace("\\", "").replace("'", "")

    time_splits = [int(x) for x in time.split(" ") if x.strip().isdigit()]

    if len(time_splits) == 0:
        return 0

    return time_splits[0] * 60 + time_splits[1] + time_splits[2] / 10


def did_start(started: str | bool) -> bool:
    if isinstance(started, bool):
        return started

    return "R" not in remove_tags(started)


def handle_startnumber(startnumber: str | int) -> int:
    if isinstance(startnumber, int):
        return startnumber

    return int(remove_tags(startnumber).strip())


# raceday_info
# ============
def handle_racetrack(racetrack: str) -> str:
    racetrack = remove_tags(racetrack)

    if "Hipòdrom " in racetrack:
        de_offset = 0

        if " de " in racetrack:
            de_offset = 3

        racetrack = racetrack[len("Hipòdrom ") + de_offset :]

    return racetrack


def handle_racedate(date: str) -> str:
    date = remove_tags(date)

    if date[4] == "-" and date[7] == "-":
        return date

    return arrow.get(date, "D-M-YYYY").format("YYYY-MM-DD")


# raceday_link
# ============
def get_raceday_id(link: str) -> str:
    return link if link.isdigit() else link[link.find("=") + 1 :]


# registration
# ============
def handle_horse_link(link: str) -> str:
    if "=" in link:
        link = link[link.find("=") + 1 :]

    if "id=" in link:
        link = link[link.find("id=") + 3 :]

    if "idcaballo" in link:
        link = link[link.rfind("=") + 1 :]

    if "&" in link:
        link = link[: link.find("&")]

    return link


# result_summary
# ==============
def handle_earnings(earnings: str | int) -> int:
    if isinstance(earnings, int):
        return earnings

    earnings = remove_tags(earnings).strip()

    if "," in earnings:
        earnings = earnings[: earnings.find(",")].strip()

    return int(earnings.replace(".", "")) if earnings != "" else 0


def handle_mark(mark: str | int | float) -> float | None:
    if isinstance(mark, (int, float)):
        return mark

    mark = remove_tags(mark).strip()

    if mark.strip() == "":
        return None

    minutes, seconds, hundreds = mark.replace("'", "").split(" ")

    return int(minutes) * 60 + int(seconds) + int(hundreds) / 100


def handle_year(year: str | int) -> int:
    if isinstance(year, int):
        return year

    year = remove_tags(year).strip()

    return int(year) if year.isnumeric() else 0
