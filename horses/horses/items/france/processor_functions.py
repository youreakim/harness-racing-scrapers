from w3lib.html import remove_tags


def handle_basic(tag: bytes) -> str:
    return remove_tags(tag).strip()


def convert_to_int(number: str | int) -> int:
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


def convert_to_float(number: str | int | float) -> int | float:
    if isinstance(number, (float, int)):
        return number

    return float(remove_tags(number).strip())


# horse_info
# ==========
def handle_horse_birthdate(date_string: str | int) -> str | None:
    if isinstance(date_string, int):
        date_string = str(date_string)

    date_string = remove_tags(date_string).strip()

    if "," in date_string and date_string[-1].isnumeric():
        date_string = date_string.split(", ")[-1]

    if len(date_string) == 4 and date_string.isnumeric():
        return f"{date_string}-01-01"

    if " - " in date_string:
        splits = [x.strip() for x in date_string.split(" - ") if x.strip().isnumeric()]

        if len(splits) == 1 and len(splits[0]) == 4:
            return f"{splits[0]}-01-01"

    return None


def handle_breed(breed: str) -> str | None:
    breed = remove_tags(breed)

    if "trotteur" in breed:
        return "standardbred"

    return None


def handle_horse_country(country_string: str) -> str:
    country_string = remove_tags(country_string)

    if " - " in country_string:
        country_string = country_string.split(" - ")[0]

        splits = [
            x
            for x in country_string.split(" ")
            if len(x.strip()) == 5 and x.strip()[0] == "("
        ]

        if len(splits) == 1:
            return splits[0][1:-1]

        if len(splits) == 0:
            return "FRA"

    if "Trotteur français" in country_string:
        return "FRA"

    if "(" in country_string:
        return country_string[country_string.find("(") + 1 : country_string.find(")")]

    return "FRA"


def handle_gender(gender_string: str) -> str:
    gender_string = remove_tags(gender_string).strip().lower()

    if " - " in gender_string:
        gender_string = gender_string.split(" - ")[0]

        splits = [
            x.strip()[1:-1]
            for x in gender_string.split(" ")
            if x.strip()[1:-1] in ["mâle", "hongre", "femelle"] and "(" in x
        ]

        if len(splits) == 1:
            gender_string = splits[0]

    if "," in gender_string and gender_string[-1].isnumeric():
        gender_string = gender_string.split(", ")[-2].strip()

    gender_string = "".join(x for x in gender_string if not x.isnumeric())

    if gender_string in ["gelding", "horse", "mare"]:
        return gender_string

    return {
        "h": "gelding",
        "m": "horse",
        "f": "mare",
        "male": "horse",
        "mâle": "horse",
        "hongre": "gelding",
        "femelle": "mare",
    }[gender_string]


def handle_horse_name(name_string: str) -> str:
    name_string = remove_tags(name_string)

    name_string = name_string.replace("*", "'")

    if name_string[0] == "&":
        name_string = name_string[name_string.find("&gt;") + 4 :]

    if " - " in name_string:
        name_string = name_string[: name_string.find(" - ")].strip()

    if "(" in name_string:
        name_string = name_string[: name_string.find("(")].strip()

    letters = [x.isalpha() or x in [" ", "'"] for x in name_string]

    if not all(letters):
        index = letters.index(False)

        name_string = name_string[:index]

    return name_string.strip().upper()


# race_info
# =========
def is_monte(monte: str | bool) -> bool:
    if isinstance(monte, bool):
        return monte

    return "icon-monte" in monte


def get_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod)

    return "mobile" if "autostart" in startmethod.lower() else "standing"


def get_distance(distance: str | int) -> int | None:
    if isinstance(distance, int):
        return distance

    distance_splits = remove_tags(distance).strip().split(" - ")

    # distance = distance[
    #     distance.find("-", distance.rfind("m") - 10) : distance.rfind("m")
    # ]
    for distance_split in distance_splits:
        distance = distance_split.strip().replace("m", "")

        if distance.isnumeric():
            return int(distance)

    return None


def get_race_purse(purse: str | int) -> int | None:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse)

    purse = [x for x in purse.split("-") if "€" in x]

    if len(purse) == 1:
        return int(purse[0].replace("€", "").strip())

    return None


def remove_racenumber(racename: str) -> str | None:
    racename = remove_tags(racename).strip()

    if racename == "":
        return None

    if racename[1].isdigit() and racename[0] == "C":
        return " ".join(racename.split(" ")[1:])

    return racename


# race_link
# =========
def shorten_race_link(link: str) -> str:
    return "/".join(link.split("/")[-3:])


# race_starter_info
# =================
def did_start(started: str | bool) -> bool:
    if isinstance(started, bool):
        return started

    started = remove_tags(started)

    return "NP" not in started.upper()


def is_starter_disqualified(is_disqualified: str | bool) -> bool:
    if isinstance(is_disqualified, bool):
        return is_disqualified

    is_disqualified = remove_tags(is_disqualified)

    return "D" in is_disqualified


def handle_starter_distance(distance: str | int) -> int:
    if isinstance(distance, int):
        return distance

    return int(remove_tags(distance).replace(" ", "").replace("\u202f", "").strip())


def handle_starter_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).strip()

    return int(finish) if finish.isnumeric() else 0


def did_finish(finished):
    if isinstance(finished, bool):
        return finished

    return True


def handle_starter_purse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse)

    return int("".join([x for x in purse if x.isdigit()]))


def handle_starter_time(time: str | int | float) -> int | float | None:
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).strip()

    if '"' in time:
        minutes = time[0]
        seconds = time[2:].replace('"', ".")

        return int(minutes) * 60 + float(seconds)

    return None


def handle_startnumber(startnumber: int | str) -> int | None:
    if isinstance(startnumber, int):
        return startnumber

    startnumber = remove_tags(startnumber).strip()

    if startnumber.isnumeric():
        return int(startnumber)

    return None


# raceday_info
# ============
def raceday_date_from_link(link: str) -> str:
    if "-" in link and "T" in link:
        return link[: link.find("T")]

    return link.split("/")[-2]


def racetrack_code_from_link(link: str) -> str:
    return link.split("/")[-1]


# raceday_link
# ============
def shorten_raceday_link(link: str) -> str:
    return "/".join(link.split("/")[-2:])


# registration
# ============
def handle_source(source: str) -> str | None:
    if source in ["arqana"]:
        return None

    return source


def shorten_horse_link(link: str) -> str | None:
    if len(link) == 6 or (len(link) == 12 and "/" not in link):
        return link

    link_parts = link.split("/")

    if "infochevaux.ifce.fr" in link or link.startswith("/fr/"):
        return link_parts[-2]

    if "/stats/chevaux/" in link:
        return "/".join(
            link_parts[
                link_parts.index("chevaux") + 1 : link_parts.index("chevaux") + 3
            ]
        )

    if "letrot.com/" in link:
        return "/".join(
            link_parts[
                link_parts.index("fiche-cheval")
                + 1 : link_parts.index("fiche-cheval")
                + 3
            ]
        )

    return None


# result_summary
# ==============
def handle_mark(mark: str | int | float) -> int | float | None:
    if isinstance(mark, (int, float)):
        return mark

    mark = remove_tags(mark).strip()

    if "'" in mark and "''" in mark:
        minutes, seconds, fraction = [int(x) for x in mark.split("'") if x != ""]

        return minutes * 60 + seconds + fraction / 10

    return None


def handle_year(year: str | int) -> int:
    if isinstance(year, int):
        return year

    year = remove_tags(year).strip()

    return int(year) if year.isnumeric() else 0


def remove_meeting(racetrack: str | bytes) -> str:
    racetrack = remove_tags(racetrack).strip()

    if racetrack[1].isdigit() and racetrack[0] == "R":
        return " ".join(racetrack.split(" ")[1:])

    return racetrack


def get_racenumber(link: str | int) -> int:
    if isinstance(link, int):
        return link

    return int(link.split("/")[-1])
