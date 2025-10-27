# horse_info
# ==========
def handle_birthdate(date_string: str) -> str | None:
    if isinstance(date_string, int) or (
        len(date_string) == 4 and date_string.isnumeric()
    ):
        return f"{date_string}-01-01"

    if len(date_string) == 10 and date_string[4] == "-":
        return date_string

    return None


def handle_name(name: str) -> str:
    if "(" in name:
        name = name[: name.find("(")]

    return name.replace("*", "").strip().upper()


def handle_country(country: str) -> str:
    if "(" in country:
        return country[country.find("(") + 1: country.find(")")]

    return "DK"


def handle_gender(gender: str) -> str:
    gender = gender.lower()

    if gender in ["gelding", "horse", "mare"]:
        return gender

    if " " in gender:
        gender = gender.split(" ")[1]

    return {
        "hingst": "horse",
        "hoppe": "mare",
        "vallak": "gelding",
        "hp": "mare",
        "h": "horse",
        "v": "gelding",
    }[gender]


# race_info
# =========
def handle_startmethod(startmethod: str) -> str:
    if len(startmethod) == 1:
        return {"A": "mobile", "V": "standing"}[startmethod]

    if "Autostart" in startmethod:
        return "mobile"

    return "standing"


def handle_racedistance(distance: str) -> int:
    return int(distance[: distance.find(" m. ")])


def is_monte(monte: str) -> bool:
    return "monté" in monte.lower()


def handle_racetype(racetype: str) -> str:
    if len(racetype) == 1:
        return "qualifier" if racetype == "k" else "race"

    if len(racetype) == 0:
        return "race"

    return (
        "qualifier"
        if "Prøveløb" in racetype or "Fremvisningsløb" in racetype
        else "race"
    )


def get_racenumber(num_string: str) -> str:
    return num_string[num_string.find("Løb ") + 4: num_string.find(".")]


def calculate_purse(purse_string: str) -> int:
    if isinstance(purse_string, list):
        if len(purse_string) == 0:
            return 0
        purse_string = purse_string[0]

    if "(" in purse_string:
        purse_string = purse_string[
            purse_string.find(":") + 1: purse_string.find(" (")
        ]
    elif "samt" in purse_string:
        purse_string = purse_string.replace(" samt ", "-")

        purse_string = purse_string[
            purse_string.find(":") + 1: purse_string.find(" ", purse_string.rfind("-"))
        ]

    return sum(int(x.replace(".", "")) for x in purse_string.split("-"))


def filter_racename(racename: str) -> str | None:
    if " kr." not in racename:
        return racename

    return None


def handle_distance(distance: str | int) -> int | None:
    if isinstance(distance, int):
        return distance

    if " m." in distance:
        return int(distance[: distance.find(" m.")])

    if "/" in distance:
        return int(distance.split("/")[1])

    if distance.isnumeric():
        return int(distance)

    return None


# race_starter_info
# =================
def handle_odds(odds: int | str) -> float | None:
    if isinstance(odds, str):
        if "(" in odds:
            odds = odds[1:-1]

            return int(odds) / 10

        if "," in odds:
            return float(odds.replace(",", "."))

        return None

    if isinstance(odds, float):
        return odds

    return odds / 10


def handle_finish(finish: str) -> int:
    if finish.isnumeric():
        return int(finish)

    return 0


def handle_purse(purse_string: str | int) -> int:
    if isinstance(purse_string, str):
        return int(purse_string.replace("kr", "").replace(" ", ""))

    return purse_string


def remove_comma(odds: str) -> str:
    if "," in odds:
        return "".join([x for x in odds[:-1] if x.isnumeric()])

    return odds


def is_approved(approved: str) -> bool:
    return "gk" in approved


def is_disqualified(place_string: str) -> bool:
    return "d" in place_string


def place(place_string: str) -> int:
    return int(place_string) if place_string.isdigit() else 0


def did_finish(time_string: str) -> bool:
    return "opg" not in time_string


def made_a_break(time_string: str) -> bool:
    return "g" in time_string.replace("opg", "")


def handle_post(post_string: str) -> str | None:
    if post_string.isdigit() and len(post_string) <= 2:
        return post_string

    if "/" in post_string:
        return post_string.split("/")[0]


def handle_racetime(time: str | int) -> float:
    if isinstance(time, str):
        if "," not in time:
            return 0

        return float(time[:4].replace(",", ".")) + 60

    if time > 3000:
        return 0

    minutes, seconds = divmod(time / 10, 100)

    return minutes * 60 + seconds


def handle_breed(breed: str) -> str | None:
    if "varmblodig" in breed:
        return "standardbred"

    return None
