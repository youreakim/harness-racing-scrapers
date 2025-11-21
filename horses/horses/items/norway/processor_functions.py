import re
import arrow
from arrow.parser import ParserMatchError
from w3lib.html import remove_tags


def handle_basic(tag: str) -> str:
    return remove_tags(tag).strip()


def convert_to_int(number: str | int) -> int:
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


def convert_to_float(number: str | int | float) -> int | float:
    if isinstance(number, (int, float)):
        return number

    return float(remove_tags(number).replace(",", ".").strip())


# horse_info
# ==========
def handle_horse_birthdate(date: str) -> str | None:
    date = remove_tags(date).strip()

    if len(date) == 4 and date.isnumeric():
        return f"{date}-01-01"

    try:
        return arrow.get(date).date().isoformat()
    except ParserMatchError:
        pass


def handle_breed(breed: str) -> str | None:
    breed = remove_tags(breed).strip()

    if breed in ["standardbred", "thoroughbred", "coldblood"]:
        return breed

    if "varmblod" in breed.lower():
        return "standardbred"
    elif "kaldblod" in breed.lower():
        return "coldblood"


def handle_horse_country(name_string: str) -> str:
    name_string = remove_tags(name_string).strip()

    if "(" in name_string:
        country_code = name_string[name_string.find("(") + 1 : name_string.find(")")]

        if "traver" in country_code.lower():
            return "NO"

        if country_code == "S":
            country_code = "SE"

        return country_code

    return "NO"


def handle_gender(gender: str) -> str:
    gender = remove_tags(gender).strip().lower()

    if gender in ["gelding", "horse", "mare"]:
        return gender

    if "-års" in gender:
        gender_splits = gender.split(" ")
        gender = gender_splits[gender_splits.index("e.") - 1]

    return {
        "v": "gelding",
        "h": "horse",
        "hp": "mare",
        "vallak": "gelding",
        "hingst": "horse",
        "hoppe": "mare",
    }[gender]


def handle_horse_name(name: str) -> str:
    name = remove_tags(name).upper()

    if "(" in name:
        name = name[: name.find("(")]

    return name.strip().replace("*", "")


# race_info
# =========
def shorten_conditions(conditions: str) -> str | None:
    conditions = remove_tags(conditions)

    conditions_parts = [
        x for x in conditions.split("\n\n") if "kr." in x or "Prøveløp" in x
    ]

    if len(conditions_parts) == 1:
        return conditions_parts[0].strip()


def get_distance(distance: str | int) -> int | None:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance)

    d = re.search(r"(\d{3,}) m\.", distance)

    if d:
        return int(d.group(1))


def get_race_purse(purse: str | int) -> int | None:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse)

    if "Premier:" in purse:
        purse_string = purse[purse.find("Premier: ") + len("Premier: ") :]

        if " premier)" in purse_string:
            purse_string = purse_string[: purse_string.find("(")]

        if " kr." in purse_string:
            purse_string = purse_string[: purse_string.rfind(" kr.")]

        return sum(
            [
                int("".join([z for z in x if z.isnumeric()]))
                for x in purse_string.split("-")
            ]
        )


def get_racenumber(number: str | int) -> int:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    return int(number.split("-")[-1])


def is_monte(monte: str | bool) -> bool:
    if isinstance(monte, bool):
        return monte

    monte = remove_tags(monte)

    return "monté" in monte.lower()


def get_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod)

    return "mobile" if "autostart" in startmethod.lower() else "standing"


def get_racetype(racetype: str) -> str:
    racetype = remove_tags(racetype)

    if "prøveløp" in racetype.lower():
        return "qualifier"
    elif "mønstringsløp" in racetype.lower():
        return "premium"

    return  "race"


# race_link
# =========
def shorten_race_link(link: str) -> str:
    return "/".join(link.split("/")[-3:])


# race_starter_info
# =================
def is_starter_disqualified(disqualified: str | bool) -> bool:
    if isinstance(disqualified, bool):
        return disqualified

    return "Disk." in remove_tags(disqualified)


def remove_license(name: str) -> str:
    name = remove_tags(name)

    if "(" in name:
        name = name[: name.find("(")]

    return name.strip()


def handle_starter_distance(distance: str | int) -> int | None:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance)

    if '/' in distance:
        distance = distance.split("/")[1].strip()

    return int(distance) if distance.isnumeric() else None


def handle_starter_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).strip()

    return int(finish) if finish.isnumeric() else 0


def did_finish(finished: str | bool) -> bool:
    if isinstance(finished, bool):
        return finished

    return "br" not in remove_tags(finished)


def did_gallop(galloped: str | bool) -> bool:
    if isinstance(galloped, bool):
        return galloped

    return "g" in remove_tags(galloped)


def handle_starter_purse(purse: str | int) -> int | None:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    if len(purse) > 0:
        return int("".join([x for x in purse.replace(",00", "") if x.isnumeric()]))


def handle_starter_time(time: str | int | float) -> int | float | None:
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).strip()

    time = "".join(x for x in time if not x.isalpha())

    if len(time) == 4 and "." in time:
        return 60 + float(time)

    if "#" not in time:
        minutes = time[0]
        seconds = time[2:].replace(",", ".")

        return int(minutes) * 60 + float(seconds)


def handle_odds(odds: str | int | float) -> int | float | None:
    if isinstance(odds, (int, float)):
        return odds

    odds = remove_tags(odds).strip()

    if "." in odds:
        return float(odds)

    return int(odds) / 10


def did_start(started: str | bool) -> bool | None:
    if isinstance(started, bool):
        return started

    return 'str' not in started.lower()


# raceday_info
# ============
def extract_racetrack_name(racetrack: str) -> str:
    racetrack = remove_tags(racetrack).strip()

    if "-" in racetrack:
        return racetrack.replace("-", " ").title()

    if racetrack == "BD":
        return "Bodø Travbane"

    if "kl. " in racetrack:
        racetrack = racetrack[:racetrack.find("kl. ")]

    return racetrack


def handle_raceday_date(date: str) -> str | None:
    if "/startlist/" in date or "/results/" in date:
        date = date[date.rfind("/") + 1:]
        
    try:
        return arrow.get(date).date().isoformat()
    except ParserMatchError:
        pass


# raceday_link
# ============
def shorten_raceday_link(link: str) -> str:
    return "/".join(link.split("/")[-3:])


# registration
# ============
def shorten_horse_link(link: str) -> str:
    link_parts = link.split("/")

    return link_parts[link_parts.index("horse") + 1]
