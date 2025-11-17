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

    number = remove_tags(number).replace(",", ".").strip()

    return float(number)


# horse_info
# ==========
def handle_horse_birthdate(date: str) -> str | None:
    date = remove_tags(date).strip()

    if "nascita" in date:
        date = date[date.find("nascita:") + 9:].strip()

    if "Sesso" in date:
        date = date[: date.find("Sesso:")].strip()

    if "/" in date:
        return arrow.get(date, "DD/MM/YYYY").format("YYYY-MM-DD")

    if date[0] == "(" and date[5] == ",":
        return f"{date[1:5]}-01-01"

    if len(date) == 4 and date.isnumeric():
        return f'{date}-01-01'

    try:
        arrow.get(date, "YYYY-MM-DD")
        return date
    except ParserMatchError:
        pass


def handle_horse_country(name_string: str) -> str:
    name_string = remove_tags(name_string).strip()

    countries = {
        'francia': 'FR',
        'italia': 'IT',
        'svezia': 'SE',
        "Stati Uniti d'America": 'US',
        'germania': 'DE',
        'norvegia': 'NO'
    }

    if "(" in name_string:
        country_code = name_string[name_string.find(
            "(") + 1: name_string.find(")")]

        return country_code

    if name_string[-1] == "-":
        country_code = name_string[name_string.find(
            "-") + 1: name_string.rfind("-")]

        return country_code

    if name_string.lower() in countries:
        return countries[name_string.lower()]

    return "IT"


def handle_gender(gender_string: str) -> str | None:
    gender_string = remove_tags(gender_string).strip().lower()

    if gender_string == "":
        return None

    if "sesso:" in gender_string:
        gender_string = gender_string[gender_string.find(
            "sesso:") + 6:].strip()

    if gender_string[0] == "(" and gender_string[5] == ",":
        gender_string = gender_string[
            gender_string.find(",") + 1: gender_string.find(".")
        ].strip()

    if gender_string in ["gelding", "horse", "mare"]:
        return gender_string

    return {
        "c": "gelding",
        "m": "horse",
        "f": "mare",
        "maschio": "horse",
        "femmina": "mare",
        "castrone": "gelding",
    }[gender_string]


def handle_horse_name(name_string: str) -> str:
    name_string = remove_tags(name_string)

    if "-" in name_string:
        name_string = name_string[: name_string.find("-")]

    if "(" in name_string:
        name_string = name_string[: name_string.find("(")]

    return name_string.replace("*", "").upper().strip()


# race_info
# =========
def get_distance(distance: str | int) -> int | None:
    if isinstance(distance, int):
        return distance

    distance = remove_tags(distance).strip()

    if "Metri" in distance:
        distance = distance[distance.find("Metri") + 6:]

        if "-" in distance:
            distance = distance[: distance.find("-")]

        if "/" in distance:
            distance = distance.split("/")[0]

    elif "mt" in distance:
        distance = distance.replace("mt", "")

    distance = distance.replace(".", "").strip()

    if distance.isnumeric():
        return int(distance)


def get_race_purse(purse: str | int) -> int | None:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse)

    purse = purse.replace(",00", "")

    purse = "".join([x for x in purse.strip() if x.isnumeric()])

    if purse != "":
        return int(purse)


def get_racename(name: str) -> str:
    name = remove_tags(name)

    if "#" in name:
        name = name[name.find(" - ") + 2:].strip()

    if name.lower().startswith("pr."):
        name = name.lower().replace("pr.", "premio ").upper().replace("  ", " ")

    return name.strip()


def get_racenumber(number: str | int) -> int:
    if isinstance(number, int):
        return number

    number = remove_tags(number)

    if "#" in number:
        number = number[number.find("#") + 1: number.find(" - ")].strip()

    elif "/n_corsa/" in number:
        splits = number.split("/")

        number = splits[splits.index("n_corsa") + 1]

    elif "corsa_" in number:
        number = number[number.find("_") + 1:].strip()

    elif number.strip().startswith("Corsa "):
        if "n. " in number:
            number = number.replace("n. ", "")

        number = number[number.find(
            "a ") + 2: number.find(" ", number.find("a ") + 2)]

    return int(number)


def get_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod)

    return "mobile" if "autostart" in startmethod.lower() else "standing"


# race_link
# =========
def shorten_race_link(link: str) -> str:
    if "index.php" in link:
        return link[link.find("/pre/") + 5:]

    if "?signature" in link:
        link = link[: link.find("?signature")]

        link_splits = link.split("/")

        return "/".join(link_splits[link_splits.index("T") + 1:])

    if 'corsa-' in link:
        return link[link.find('-') + 1:]

    return "".join(link.split("/")[-3:])


# race_starter_info
# =================
def is_starter_disqualified(disqualified: str | bool) -> bool:
    if isinstance(disqualified, bool):
        return disqualified

    disqualified = remove_tags(disqualified).strip().upper()

    return "RP" in disqualified


def handle_person_name(name: str) -> str:
    name = remove_tags(name)

    if "(" in name:
        name = name[: name.find("(")]

    return name.strip()


def handle_starter_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish if finish < 99 else 0

    finish = remove_tags(finish).replace("°", "").strip()

    return int(finish) if finish.isnumeric() else 0


def did_finish(finished: str | bool) -> bool:
    if isinstance(finished, bool):
        return finished

    finished = remove_tags(finished)

    return "rt" not in finished.lower()


def did_gallop(galloped: str | bool) -> bool:
    if isinstance(galloped, bool):
        return galloped

    galloped = remove_tags(galloped)

    return "rp" in galloped.lower()


def handle_starter_purse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    return (
        int("".join([x for x in purse.replace(",00", "") if x.isnumeric()]))
        if purse != ""
        else 0
    )


def handle_starter_time(time: str | int | float) -> int | float | None:
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).strip()

    if "," in time and "." in time:
        minutes = time[0]
        seconds = time[2:].replace(",", ".")

        return int(minutes) * 60 + float(seconds)

    if "." in time and time != ".":
        if time[1] == "." and time[-2] == ".":
            return 60 * int(time[0]) + float(time[2:])
        return 60 + float(time)

    if time.isnumeric() and len(time) == 6:
        return int(time[1]) * 60 + int(time[2:4]) + int(time[4:]) / 100


def did_start(started: str | bool) -> bool:
    if isinstance(started, bool):
        return started

    started = remove_tags(started).upper().strip()

    return (
        False
        if len(started) == 0 or "NP" in started or started in ["NON PARTENTE", "RC"]
        else True
    )


def handle_startnumber(startnumber: str) -> str | None:
    if isinstance(startnumber, int):
        return startnumber

    startnumber = remove_tags(startnumber).strip()

    while startnumber[0] == "0":
        startnumber = startnumber[1:]

    if startnumber.isnumeric():
        return startnumber


# raceday_info
# ============
def handle_raceday_date(date_string: str) -> str | None:
    date_string = remove_tags(date_string)

    if "hPart.php" in date_string:
        date_string = date_string[
            date_string.find("data=") + 5: date_string.find("&ippodromo")
        ]

        return date_string

    if "DATA" in date_string:
        date_string = date_string[
            date_string.find("DATA=") + 5: date_string.find("&IPPO")
        ].strip()

        return arrow.get(date_string, "DDMMYY").format("YYYY-MM-DD")

    if "ippica" in date_string:
        date_string = date_string[date_string.rfind(
            "/") + 1: date_string.find("?")]

        return date_string

    if "/" in date_string:
        return arrow.get(date_string, "DD/MM/YYYY").format("YYYY-MM-DD")

    if date_string[2] == "-" and date_string[5] == "-":
        return "-".join(reversed(date_string.split("-")))

    try:
        arrow.get(date_string, "YYYY-MM-DD")
        return date_string
    except ParserMatchError:
        pass

    try:
        d = arrow.get(date_string, 'dddd DD MMMM YYYY', locale='it_IT')
        return d.format('YYYY-MM-DD')
    except ParserMatchError:
        pass


def handle_racetrack(racetrack: str) -> str | None:
    racetrack = remove_tags(racetrack).strip().upper()

    if racetrack in ["", "FRANCIA", "ESTERO"]:
        return None

    return {
        "AVERSA": "AVERSA",
        "ROMA": "ROMA",
        "VILLANOVA": "VILLANOVA",
        "BOLOGNA": "BOLOGNA",
        "CASTELLUCCIO": "CASTELLUCCIO",
        "VILLANOVA D'ALBENGA": "VILLANOVA",
        "FOGGIA": "CASTELLUCCIO",
        "ROMA, CAPANNELLE": "ROMA",
        "AVERSA, CIRIGLIANO": "AVERSA",
        "ALBENGA, DEI FIORI": "VILLANOVA",
        "CASTELLUCCIO DEI SAURI, DEI SAURI": "CASTELLUCCIO",
        "BOLOGNA, ARCOVEGGIO": "BOLOGNA",
        "ALBENGA": "VILLANOVA",
        "CASTELLUCCIO DEI SAURI": "CASTELLUCCIO",
        "FOLLONICA": "FOLLONICA",  # nya
        "MILANO": "MILANO",
        "NAPOLI": "NAPOLI",
        "TREVISO": "TREVISO",
        "PALERMO": "PALERMO",
        "PADOVA": "PADOVA",
        "SIRACUSA": "SIRACUSA",
        "TORINO": "TORINO",
        "TARANTO": "TARANTO",
        "MODENA": "MODENA",
        "FIRENZE": "FIRENZE",
        "CESENA": "CESENA",
        "PONTECAGNANO": "PONTECAGNANO",
        "MONTEGIORGIO": "MONTEGIORGIO",
        "MONTECATINI TERME": "MONTECATINI",
        "MONTECATINI": "MONTECATINI",
        "SS.COSMA-DAMIANO": "GARIGLIANO",
        "SANTI COSMA E DAMIANO": "GARIGLIANO",
        "GARIGLIANO": "GARIGLIANO",
        "SS.COSMA E DAMIANO": "GARIGLIANO",
        "CASARANO": "CASARANO",
        "TRIESTE": "TRIESTE",
        "FERRARA": "FERRARA",
    }[racetrack]


# raceday_link
# ============
def shorten_raceday_link(link: str) -> str:
    if "ippica" in link:
        link = link[link.find("/T/") + 3:]

    if "hPart.php" in link:
        link = link[link.find("?") + 1:]

    if "anact" in link:
        link = link[link.find("?") + 1:]

    if '#ippodromo' in link:
        link = link[link.find('-') + 1:]

    return link.strip()


# registration
# ============
def shorten_horse_link(link: str) -> str:
    if "?nome_cav" in link:
        return link.split("=")[1].replace("'", "\'")

    if "Codice" in link:
        return link[link.find("Codice:") + 7:].strip()

    if "snai" in link:
        link_splits = link.split("/")

        return link_splits[link_splits.index("T") + 1]

    if "id_cav" in link:
        return link[link.find("=") + 1:]

    if "ID" in link:
        link = link[link.find("ID=") + 3:]

        if "ElencoPerf" in link:
            link = link[: link.find("'")]

        return link

    if "COD" in link:
        link = link[link.find("COD=") + 4:]

        if "Scheda_Cavallo" in link:
            link = link[: link.find("'")]

        return link

    if "?codice" in link:
        return link.split("=")[1]

    return link


def extract_registration(reg: str) -> str | None:
    if "Codice" in reg:
        return reg[reg.find("Codice:") + 7:]

    if "?codice" in reg:
        return reg.split("=")[1]

    return None


# result_summary
# ==============
def handle_earnings(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    if "," in purse:
        purse = purse[: purse.find(",")]

    return int(remove_tags(purse).strip().replace(".", ""))


def handle_mark(mark: str | int | float) -> int | float | None:
    if isinstance(mark, (int, float)):
        return mark

    mark = remove_tags(mark).strip()

    if mark == "0":
        return None

    if mark[1] == "." and mark[4] == ".":
        minutes, seconds = int(mark[0]), float(mark[2:])

        return minutes * 60 + seconds
