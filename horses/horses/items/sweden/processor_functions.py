import re
import arrow
from arrow.parser import ParserMatchError


# horse_info
# ==========
def handle_name(name: str) -> str:
    if "(" in name:
        name = name[: name.find("(")]

    name = name.translate(str.maketrans({"`": "'", "†": None, "*": None}))

    return name.replace("*", "").strip().upper()


def handle_gender(gender: str) -> str | None:
    return {
        "ZZ": None,
        "S": "mare",
        "H": "horse",
        "V": "gelding",
        "stallion": "horse",
        "gelding": "gelding",
        "mare": "mare",
        "horse": "horse",
    }[gender]


def handle_country(name_string: str) -> str | None:
    if name_string == "ZZ":
        return None

    if len(name_string) == 2 and name_string not in [
        "EM",
        "IA",
        "YA",
        "HÅ",
        "HE",
        "YR",
        "TY",
    ]:
        return name_string

    if "(" in name_string:
        return name_string[name_string.find("(") + 1 : -1]

    return "SE"


def handle_breed(breed: str) -> str | None:
    if len(breed) == 1:
        return {"V": "standardbred", "K": "coldblood"}[breed]

    if "varmblod" in breed.lower():
        return "standardbred"
    elif "kallblod" in breed.lower():
        return "coldblood"


def handle_birthdate(date_string: str) -> str | None:
    if isinstance(date_string, int) or (len(date_string) == 4 and date_string.isdigit()):
        return f"{date_string}-01-01"

    try:
        return arrow.get(date_string).date().isoformat()
    except ParserMatchError:
        pass


def filter_breeder(breeder: str) -> str | None:
    if "uppgift saknas" not in breeder.lower():
        return breeder


# race_info
# =========
def get_distance(distance: str | int) -> int | None:
    if isinstance(distance, int):
        return distance

    if distance.isnumeric():
        return int(distance)

    match = re.search(r"(\d{4}) m\.", distance)

    if match:
        return int(match.group(1))

    distance_splits = distance.split("/")

    if len(distance_splits[1]) <= 4 and distance_splits[1].isnumeric():
        return int(distance_splits[1])


def is_monte(conditions: str | bool) -> bool:
    if isinstance(conditions, bool):
        return conditions

    return "montélopp" in conditions.lower()


def handle_racetype(code: str) -> str | None:
    if code in ["race", "qualifier", "premium"]:
        return code

    if len(code) == 1:
        return {"V": "race", "K": "qualifier", "P": "premium"}[code]

    if "\n" in code:
        if "kvallopp" in code.lower():
            return "qualifier"
        elif "premielopp" in code.lower():
            return "premium"
        else:
            return "race"


def handle_startmethod(conditions: str) -> str:
    if conditions in ["volte", "auto", "line"]:
        return {"volte": "standing", "auto": "mobile", "line": "line"}[conditions]

    if "autostart" in conditions.lower():
        return "mobile"

    return "standing"


def handle_race_purse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    return int("".join(x for x in purse if x.isnumeric()))


# race_starter_info
# =================
def is_approved(place: str | bool) -> bool | None:
    if isinstance(place, bool):
        return place

    if "g" in place:
        return "gdk" in place
    elif "p" in place:
        return "ej" not in place


def is_disqualified(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value

    return "d" in value and "dist" not in value


def remove_licence(name: str) -> str:
    if name[-2] == " " and name[-1].islower():
        return name[:-2]

    return name


def did_finish(time_string: str | bool) -> bool:
    if isinstance(time_string, bool):
        return time_string

    return "u" not in time_string.replace("kub", "") and "vänd" not in time_string


def handle_finish(place: str | int) -> int:
    if isinstance(place, int):
        return place if place < 20 else 0

    return int(place) if place.isdigit() and int(place) < 20 else 0


def did_gallop(time_string: str | bool) -> bool:
    if isinstance(time_string, bool):
        return time_string

    return "g" in time_string


def handle_odds(odds: str | int | float) -> int | float:
    if isinstance(odds, (int, float)):
        return odds

    if "(" in odds:
        return int(odds.strip()[1:-1])
    elif "," in odds:
        return float(odds.replace(",", "."))

    return int(odds) / 10


def handle_postposition(postposition: str | int) -> int | None:
    if isinstance(postposition, int):
        return postposition if postposition < 20 else None

    if "/" in postposition:
        postposition = int(postposition.split("/")[0])
        return postposition if postposition < 20 else None


def handle_racetime(timevalue: str | int | float) -> int | float:
    if isinstance(timevalue, str):
        if "," in timevalue:
            timevalue = int("".join([x for x in timevalue if x.isdigit()])) + 1000
        elif timevalue.isdigit():
            timevalue = int(timevalue)
        else:
            return 0

    elif isinstance(timevalue, float):
        return timevalue

    if timevalue > 9000:
        return 0

    minutes, timevalue = divmod(timevalue, 1000)
    seconds, timevalue = divmod(timevalue, 10)

    return minutes * 60 + seconds + timevalue / 10
