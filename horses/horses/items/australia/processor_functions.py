import arrow
from w3lib.html import remove_tags


def handle_basic(tag: str) -> str:
    return remove_tags(tag).replace("\xa0", "").strip()


# horse_info
# ==========
def handle_horse_name(name_string: str) -> str:
    name_string = remove_tags(name_string)

    if "(" in name_string:
        name_string = name_string[: name_string.find("(")]

    return name_string.replace("*", "").strip().upper()


def handle_horse_country(name_string: str) -> str | None:
    name_string = remove_tags(name_string)

    if "(" in name_string:
        country_code = name_string[name_string.find("(") + 1 : name_string.find(")")]

        if country_code.lower() != "thor" or all(
            not x.isnumeric() for x in country_code
        ):
            return country_code

    else:
        return "AUS"

    return None


def handle_horse_birthdate(date_string: str) -> str | None:
    date_string = remove_tags(date_string)

    if len(date_string) == 4 and date_string.isnumeric():
        return f"{date_string}-01-01"

    date_format = "DD-MMM-YYYY"

    date_splits = date_string.split("-")

    if (
        len(date_string) == 10
        and all(x.isnumeric() for x in date_string.split("-"))
        and len(date_splits) == 3
    ):
        date_format = "YYYY-MM-DD"

    try:
        return arrow.get(date_string, date_format).format("YYYY-MM-DD")
    except (arrow.parser.ParserError, arrow.parser.ParserMatchError):
        return None


def handle_gender(gender_string: str) -> str | None:
    gender_string = remove_tags(gender_string).lower()

    if gender_string == "":
        return None

    if gender_string in ["gelding", "horse", "mare"]:
        return gender_string

    if " " in gender_string:
        if "mare" in gender_string or "filly" in gender_string:
            return "mare"
        if "horse" in gender_string or "colt" in gender_string:
            return "horse"
        if "gelding" in gender_string:
            return "gelding"

    return {"g": "gelding", "h": "horse", "m": "mare", "f": "mare", "r": "horse"}[
        gender_string
    ]


def handle_breed(breed):
    breed = remove_tags(breed)

    return breed if breed in ["standardbred", "thoroughbred", "coldblood"] else None


def handle_breeder(breeder: str) -> str:
    breeder = remove_tags(breeder)

    if "Breeder(s):" in breeder:
        breeder = breeder[breeder.find(":") + 1 :]

    return breeder.strip()


# race_info
# =========
def get_race_type(race_type: str) -> str:
    if race_type in ["race", "qualifier"]:
        return race_type

    return "qualifier" if "teal" in race_type else "race"


def get_distance(distance: int | str) -> int:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance)

    return int(distance.lower().replace("m", ""))


def get_race_purse(purse: int | str) -> int | None:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    if purse[0] == "$":
        if "\n" in purse:
            purse = purse[: purse.find("\n")]

        return int("".join([x for x in purse if x.isnumeric()]))

    return None


def get_racenumber(racenumber: str | int) -> int:
    if isinstance(racenumber, int):
        return racenumber

    racenumber = remove_tags(racenumber)

    return int(racenumber)


def get_startmethod(race_information: str) -> str:
    race_information = remove_tags(race_information)

    return "mobile" if "mobile" in race_information.lower() else "standing"


def get_gait(racename: str) -> str:
    racename = remove_tags(racename)

    return "pace" if "pace" in racename.lower() else "trot"


# race_link
# =========
def shorten_race_link(link: str) -> str:
    if "=" in link:
        link = link[link.find("=") + 1 :]

    return link


# race_starter_info
# =================
def is_starter_disqualified(res: str | bool) -> bool:
    if isinstance(res, bool):
        return res

    res = remove_tags(res)

    return "d" in res


def handle_person(person: str) -> str:
    person = remove_tags(person)

    if "(" in person:
        person = person[: person.find("(")]

    return person.strip()


def handle_starter_distance(distance: str | int) -> int:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance).replace("m", "").replace("-", "").strip()

    return int(distance) if distance.isnumeric() else 0


def handle_starter_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).strip()

    return int(finish) if finish.isnumeric() else 0


def did_finish(finish: str | bool) -> bool:
    if isinstance(finish, bool):
        return finish

    finish = remove_tags(finish)

    return "pulled" not in finish.lower()


def did_gallop(broke: str | bool) -> bool:
    if isinstance(broke, bool):
        return broke

    broke = remove_tags(broke)

    return "break" in broke or "broke" in broke


def handle_starter_purse(purse: str | int) -> int | None:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    if len(purse) > 0:
        return int("".join([x for x in purse if x.isnumeric()]))

    return None


def handle_starter_time(time: str | int | float) -> float | None:
    if isinstance(time, (int, float)):
        return round(time, ndigits=1)

    time = remove_tags(time).replace("\r\n", "").strip()

    if time[:2] == "TR":
        time = time[2:]

    if ":" in time:
        minutes = time[0]
        seconds = time[2:].replace(":", ".")

        return int(minutes) * 60 + float(seconds)

    if "." in time and 2 < len(time) < 5:
        return round(float(time), ndigits=1)

    return None


def handle_win_odds(odds: str | int | float) -> float | None:
    if isinstance(odds, (int, float)):
        return odds

    odds = remove_tags(odds).replace("\xa0", "").strip()

    if odds != "":
        return float("".join([x for x in odds if x.isnumeric() or x == "."]))

    return None


def did_start(started: str | bool) -> bool | None:
    if isinstance(started, bool):
        return started

    return None


def handle_startnumber(startnumber: str | int) -> int:
    if isinstance(startnumber, int):
        return startnumber

    startnumber = remove_tags(startnumber)

    return int(startnumber.strip())


# race_time
# =========
def handle_race_time(time: str | int | float) -> float:
    if isinstance(time, (float, int)):
        return time

    time = remove_tags(time)

    if ":" in time:
        time_splits = [int(x) for x in time.split(":")]

        return time_splits[0] * 60 + time_splits[1] + time_splits[2] / 10

    return float(time.strip())


# raceday_info
# ============
def handle_raceday_date(date_string: str) -> str | None:
    date_string = remove_tags(date_string).replace("\r\n", "").strip()

    if "?firstDate=" in date_string:
        return arrow.get(date_string[date_string.find("=") + 1 :], "DD-MM-YYYY").format(
            "YYYY-MM-DD"
        )

    if date_string[0].isalpha() and date_string[-2].isnumeric():
        date_string = "".join([x for x in date_string if x.isnumeric()])

        return arrow.get(date_string, "DDMMYY").format("YYYY-MM-DD")

    try:
        d = arrow.get(date_string, "DD-MMM-YYYY").format("YYYY-MM-DD")
        return d
    except ValueError:
        try:
            arrow.get(date_string)
            return date_string
        except ValueError:
            pass

    return None


# raceday_link
# ============
def shorten_raceday_link(link: str) -> str:
    if "=" in link:
        link = link[link.find("=") + 1 :]

    return link


# registration
# ============
def shorten_horse_link(link: str) -> str:
    if link.isnumeric():
        return link

    link = remove_tags(link)

    link = link.split("/")[-1]

    return link[link.rfind("=") + 1 :] if "=" in link else link
