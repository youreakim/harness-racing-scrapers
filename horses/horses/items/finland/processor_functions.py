def is_empty(value: str) -> str | None:
    if value.strip() != "-":
        return value.strip()

    return None


# horse_info
# ==========
def handle_birthdate(birthdate: str | int) -> str | None:
    if isinstance(birthdate, int) or (birthdate.isdigit() and len(birthdate) == 4):
        return f"{birthdate}-01-01"

    if len(birthdate.split("-")) == 3 and len(birthdate) == 12:
        return birthdate

    if "." in birthdate:
        return "-".join(reversed(birthdate.split(".")))

    return None


def handle_breed(breed: str) -> str:
    breed = breed.lower()

    if breed in ["coldblood", "standardbred", "thoroughbred"]:
        return breed

    return {
        "lämminverinen": "standardbred",
        "suomenhevonen": "coldblood",
        "kylmäverinen": "coldblood",
        "l": "standardbred",
        "s": "coldblood",
        "k": "coldblood",
    }[breed]


def handle_gender(gender: str) -> str:
    gender = gender.lower()

    if gender in ["gelding", "horse", "mare"]:
        return gender

    return {
        "r": "gelding",
        "t": "mare",
        "o": "horse",
        "ruuna": "gelding",
        "tamma": "mare",
        "ori": "horse",
    }[gender]


def handle_name(name: str) -> str:
    if "(" in name:
        name = name[: name.find("(")]

    return name.replace("*", "").upper().strip()


def check_ueln(ueln: str) -> str | None:
    ueln = ueln.strip()

    return ueln if len(ueln) == 15 else None


# race_info
# =========
def handle_racetype(racetype: str) -> str:
    return {
        "koe": "qualifier",
        "opetus": "opetus",
        "nuoret": "nuoret",
        "toto": "race",
        "lounas": "race",
        "paikallis": "race",
    }[racetype.strip().lower()]


def handle_startmethod(startmethod: str) -> str:
    return {
        "tasoitusajo": "standing",
        "ryhmalahto": "mobile",
        "linjalähtö": "line",
        "linjalahto": "line",
    }[startmethod.strip().lower()]


# race_starter_info
# =================
def handle_racetime(time: str | int | float) -> float | int:
    if isinstance(time, (int, float)):
        return time

    return int(time[0]) * 60 + float(time[2:])


def is_disqualified(disqualified: str | bool) -> bool:
    if isinstance(disqualified, bool):
        return disqualified

    return disqualified != ""
