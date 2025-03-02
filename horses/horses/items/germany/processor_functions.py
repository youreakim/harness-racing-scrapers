import arrow
from w3lib.html import remove_tags


def handle_basic(tag: str) -> str:
    return remove_tags(tag).strip()


def remove_non_breaking_space(tag: str) -> str:
    return remove_tags(tag).replace("\xa0", " ").strip()


def convert_to_float(number: str | int | float) -> int | float:
    if isinstance(number, (int, float)):
        return number

    number = remove_tags(number).replace(",", ".").strip()

    return float(number) if number.isnumeric() else 0


def convert_to_int(number: str | int) -> int:
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


# horse_info
# ==========
def handle_birthdate(date_string: str | int) -> str | None:
    if isinstance(date_string, int):
        return f"{date_string}-01-01"

    date_string = remove_tags(date_string).strip()

    if "." in date_string:
        return "-".join(reversed(date_string.split(".")))

    if len(date_string) == 4 and date_string.isdigit():
        return f"{date_string}-01-01"

    if len(date_string) == 10 and len(date_string.split("-")) == 3:
        return date_string

    return None


def remove_title(value: str) -> str:
    value = remove_tags(value)

    if ":" in value:
        value = value[value.find(":") + 1 :]

    return value.strip()


def handle_name(name: str) -> str:
    name = remove_tags(name)

    if "(" in name:
        name = name[: name.find("(")]

    elif "[" in name:
        name = name[: name.find("[")]

    return name.strip()


def handle_country(name: str) -> str | None:
    name = remove_tags(name)

    country = "DE"

    if "(" in name:
        country = name[name.find("(") + 1 : name.find(")")]

    elif "[" in name:
        country = name[name.find("[") + 1 : name.find("]")]

    if len(country) == 2:
        return country

    return None


def handle_gender(gender: str) -> str:
    gender = remove_tags(gender).strip()

    if gender in ["gelding", "horse", "mare"]:
        return gender

    if ". v. " in gender:
        gender = gender[gender.find(". v. ") - 1]

    return {
        "S": "mare",
        "H": "horse",
        "W": "gelding",
        "Stute": "mare",
        "Hengst": "horse",
        "Wallach": "gelding",
    }[gender]


# race_info
# =========
def handle_distance(distance: str | int) -> int:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance)

    if ":" in distance:
        distance = distance[distance.find(":") + 1 :]

    if "/" in distance:
        distance = distance[: distance.find("/")]

    if "m" in distance:
        distance = distance.replace("m", "")

    return int(distance.replace(".", "").strip())


def handle_racepurse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    if "€" in purse:
        purse = purse[: purse.find("€")]

    if ":" in purse:
        purse = purse[purse.find(":") + 1 :]

    return int(purse.replace(".", "").strip())


def get_racenumber(number: str | int) -> int | None:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    return int(number) if number.isdigit() else None


def get_racetype(num_string: str) -> str:
    num_string = remove_tags(num_string).strip()

    return (
        "qualifier"
        if "q" in num_string.lower()
        or num_string.lower() in ["p", "a", "", "pl", "wq", "az"]
        else "race"
    )


def get_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod).strip()

    return "mobile" if startmethod == "A" else "standing"


# race_link
# =========
def shorten_race_link(url: str) -> str:
    return "/".join(url.split("/")[-4:])


# race_starter_info
# =================
def is_disqualified(disqualified: str | bool) -> bool:
    if isinstance(disqualified, bool):
        return disqualified

    disqualified = remove_tags(disqualified)

    return "dis" in disqualified


def handle_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).replace(".", "").strip()

    return int(finish) if finish.isnumeric() else 0


def handle_racetime(racetime: str | int | float) -> int | float | None:
    if isinstance(racetime, (int, float)):
        return racetime

    racetime = remove_tags(racetime).strip()

    minutes = 0

    if ":" in racetime:
        minutes, racetime = racetime.split(":")

    if "," in racetime:
        return int(minutes) * 60 + float(racetime.replace(",", "."))

    return None


def handle_show_odds(number: str | int | float) -> int | float:
    if isinstance(number, (int, float)):
        return number

    number = remove_tags(number).strip()

    if "," in number:
        return float(number.replace(",", "."))

    return int(number) / 10 if number.isnumeric() else 0


def handle_purse(purse_string: str | int) -> int:
    if isinstance(purse_string, int):
        return purse_string

    purse_string = remove_tags(purse_string).replace(".", "").replace("€", "").strip()

    return int(purse_string) if purse_string.isnumeric() else 0


def handle_startnumber(number: str | int) -> int | None:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    return int(number) if number.isnumeric() else None


# raceday_info
# ============
def handle_racedate(date_string: str) -> str | None:
    date_string = remove_tags(date_string).strip()

    if "." in date_string:
        return arrow.get(date_string, "DD.MM.YYYY").format("YYYY-MM-DD")

    if "/" in date_string:
        date_string = date_string.split("/")[-2]

        return arrow.get(date_string, "YYYYMMDD").format("YYYY-MM-DD")

    return None


def handle_racetrack(racetrack: str) -> str:
    racetrack = remove_tags(racetrack).strip()

    if " › " in racetrack:
        racetrack = racetrack[: racetrack.find(" › ")]

    if "(" in racetrack:
        racetrack = racetrack[: racetrack.find("(")].strip()

    return racetrack


def handle_raceday_country(racetrack: str) -> str:
    racetrack = remove_tags(racetrack).strip()

    if "(" in racetrack:
        return racetrack[racetrack.find("(") + 1 : racetrack.find(")")]

    return "Germany"


def find_racetrack_code(url: str) -> str:
    url_splits = url.split("/")

    return url_splits[-3] if url_splits[-5] == "bc" else url_splits[-4]


# raceday_link
# ============
def shorten_raceday_link(url: str) -> str:
    first = -4 if "/bc/" not in url else -5

    return "/".join(url.split("/")[first:-1])


# registration
# ============
def handle_link(link: str) -> str:
    link = remove_tags(link)

    if ":" in link:
        link = link[link.find(":") + 1 :]

    return link


def handle_odds(number: str | int | float) -> int | float:
    if isinstance(number, (int, float)):
        return number

    number = number.replace(",", ".")

    return float(number) if number.replace(".", "").isnumeric() else 0
