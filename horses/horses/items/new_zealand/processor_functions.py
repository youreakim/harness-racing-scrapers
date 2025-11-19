import html
import arrow
from arrow.parser import ParserMatchError
from w3lib.html import remove_tags


def handle_basic(tag: str) -> str:
    return remove_tags(tag).strip().replace("\xa0", " ")


def convert_to_int(number: str | int) -> int:
    if isinstance(number, int):
        return number

    return int(remove_tags(number).strip())


def convert_to_float(number: str | int | float) -> int | float:
    if isinstance(number, (int, float)):
        return number

    return float(remove_tags(number).strip())


# horse_info
# ==========
def handle_horse_birthdate(date: str) -> str | None:
    # Needs to be adapted to southern hemisphere breeding season
    date = remove_tags(date).strip()

    if len(date) == 4 and date.isnumeric():
        return f"{date}-01-01"

    try:
        return arrow.get(date, "DD-MM-YYYY").format("YYYY-MM-DD")
    except ParserMatchError:
        pass


def handle_breed(breed: str) -> str | None:
    if breed in ["standardbred", "thoroughbred", "coldblood"]:
        return breed


def handle_breeder(breeder: str) -> str:
    breeder = remove_tags(breeder)

    if "Breeder: " in breeder:
        breeder = breeder[breeder.find(":") + 1:]

    return breeder.strip()


def handle_chip(chip: str) -> str | None:
    chip = remove_tags(chip).strip()

    if "N/A" not in chip:
        return chip


def handle_gender(gender: str) -> str:
    gender = remove_tags(gender).strip().lower()

    if gender in ["gelding", "horse", "mare"]:
        return gender

    if gender[0].isnumeric() and " " in gender:
        gender = gender.split(" ")[-1]

    if "(" in gender:
        gender = gender[: gender.find("(")]

    return {
        "g": "gelding",
        "h": "horse",
        "c": "horse",
        "m": "mare",
        "f": "mare",
        "r": "horse",
    }[gender]


def handle_horse_name(name: str) -> str:
    name = remove_tags(name).strip()

    if "(" in name:
        name = name[: name.find("(")]

    return name.replace("*", "").strip().upper()


def handle_country(country: str) -> str | None:
    if "." in country:
        country = country[: country.find(".")]

    if "(" in country:
        country = country[country.find("(") + 1:country.find(")")]

    # Remove indications of Embryo Transfer and Thoroughbreds
    if country.upper() in ["ET", "THOR"]:
        return None

    return country


# race_info
# =========
def get_distance(distance: str | int) -> int:
    if isinstance(distance, int):
        return distance

    return int(remove_tags(distance).replace("m", "").strip())


def get_race_purse(purse: str | int) -> int:
    if isinstance(purse, int):
        return purse

    purse = remove_tags(purse).strip()

    if '.' in purse:
        purse = purse[: purse.find(".")]

    return int(purse.replace(",", "").replace("$", ""))


def get_racenumber(number: str | int) -> int:
    if isinstance(number, int):
        return number

    number = remove_tags(number).strip()

    return int(number.split("-")[-1])


def get_startmethod(startmethod: str) -> str:
    startmethod = remove_tags(startmethod)

    return "mobile" if "mob" in startmethod.lower() else "standing"


def get_gait(gait: str) -> str:
    gait = remove_tags(gait)

    return "pace" if "pace" in gait.lower() else "trot"


def handle_conditions(conditions: str) -> str:
    return html.unescape(conditions)


# race_link
# ========= 
def shorten_race_link(link: str) -> str:
    link = link[
        link.find("=", link.find("RacehdrID"))
        + 1 : link.find("&", link.find("RacehdrID") + 12)
    ]

    return link


# race_starter_info
# =================
def handle_startnumber(number: str | int) -> int:
    if isinstance(number, int):
        return number

    number = remove_tags(number)

    if "scr" in number.lower():
        return 0

    return int(number)


def is_starter_disqualified(disqualified: bool) -> bool | None:
    if isinstance(disqualified, bool):
        return disqualified


def remove_license(name: str) -> str:
    name = remove_tags(name)

    if "(" in name:
        name = name[: name.find("(")]

    return name.strip()


def did_finish(finished: str | bool) -> bool:
    if isinstance(finished, bool):
        return finished

    finished = remove_tags(finished)

    return "pup" not in finished


def handle_starter_finish(finish: str | int) -> int:
    if isinstance(finish, int):
        return finish

    finish = remove_tags(finish).strip()

    return int(finish) if finish.isnumeric() else 0


def did_gallop(galloped: str | bool) -> bool | None:
    if isinstance(galloped, bool):
        return galloped


def handle_starter_purse(purse: str | int | float) -> int | float:
    if isinstance(purse, (int, float)):
        return purse

    purse = remove_tags(purse).replace(",", "").replace("$", "").strip()

    return float(purse)


def handle_starter_time(time: str | int | float) -> int | float | None:
    if isinstance(time, (int, float)):
        return time

    time = remove_tags(time).strip()

    if "-" in time:
        minutes = time[0]
        seconds = time[2:]

        return int(minutes) * 60 + float(seconds)


# raceday_info
# ============
def handle_date(date_string: str) -> str | None:
    date_string = remove_tags(date_string)

    date_string = date_string.replace("\xa0", " ").strip()

    if len(date_string.split(" ")) == 4:
        return arrow.get(date_string, "ddd DD MMM YYYY").format("YYYY-MM-DD")

    if len(date_string) == 10 and date_string[4] == "-" and date_string[7] == "-":
        return date_string

    if date_string[0].isnumeric():
        return arrow.get(date_string, "DD MMM YYYY").format("YYYY-MM-DD")
    else:
        d = arrow.get(f"{date_string} {arrow.utcnow().year}", "ddd D MMM YYYY")

        if d.format("ddd") != date_string[:3]:
            d = d.shift(years=1)

        return d.format("YYYY-MM-DD")


# raceday_link
# ============
def shorten_raceday_link(link: str) -> str:
    if "RacedayID" in link:
        link = link[
            link.find("=", link.find("RacedayID"))
            + 1 : link.find("&", link.find("RacedayID") + 12)
        ]

    return link


# registration
# ============
def shorten_horse_link(link: str) -> str | None:
    if "HorseI" in link:
        return link[
            link.find("=", link.find("HorseI"))
            + 1 : link.find("&", link.find("HorseI") + 10)
        ]


# result_summary
# ==============
def handle_earnings(purse: str | int | float) -> int | float:
    if isinstance(purse, (int, float)):
        return purse

    purse = remove_tags(purse).strip()

    if "Lt $" in purse:
        purse = purse[purse.find("$"):purse.find("Win")].strip()

    return int(purse.replace("$", "").replace(",", ""))


def handle_year(year: str | int) -> int | None:
    if isinstance(year, int):
        return year

    year = remove_tags(year).strip()

    if "yo" in year:
        year = year[: year.find(" ")]

    if year.isnumeric():
        return int(year)


def handle_mark(mark: str | int | float) -> int | float | None:
    if isinstance(mark, (int, float)):
        return mark

    m = 0

    mark = html.unescape(remove_tags(mark).replace("(", "").replace(")", "").replace("*", ""))

    for mark_string in mark.split("&"):
        minutes, seconds = mark_string.split(".", 1)

        if "," in seconds:
            seconds = seconds[:seconds.find(",")]

        seconds = "".join(x for x in seconds if not x.isalpha())

        time = int(minutes) * 60 + float(seconds)

        if m == 0 or time < m:
            m = time

    return m


def handle_placings(placing: str | int) -> int:
    if isinstance(placing, int):
        return placing

    placing = ''.join(x for x in placing if x.isnumeric())

    return int(placing) if len(placing) > 0 else 0
