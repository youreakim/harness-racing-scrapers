import json

import arrow
from horses.items.denmark import (
    DanishHorse,
    DanishHorseInfo,
    DanishRace,
    DanishRaceday,
    DanishRacedayInfo,
    DanishRacedayLink,
    DanishRaceInfo,
    DanishRaceLink,
    DanishRaceStarter,
    DanishRaceStarterInfo,
    DanishRegistration,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response


def parse_calendar(response: Response) -> list[dict]:
    response_json = json.loads(response.body)

    racedays = []

    for raceday_json in response_json:
        raceday = parse_raceday(raceday_json)

        url = f"https://api.danskhv.dk/webapi/trot/raceinfo/{
            raceday.get_output_value('links')[0]['link']}/startlists"

        key = f"{raceday.get_output_value('raceday_info')['date']}_{
            raceday.get_output_value('raceday_info')['racetrack']}"

        racedays.append({"raceday": raceday, "url": url, "key": key})

    return racedays


def parse_races(response: Response, raceday: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for race_json in response_json["raceList"]:
        race = parse_race(race_json)

        for starter_json in race_json.get("horses", []):
            parse_starter(starter_json, race)

        for scratched_json in race_json.get("withdrawnHorses", []):
            parse_scratched(scratched_json, race)

        raceday.add_value("races", race.load_item())


def parse_raceday(raceday_json: dict) -> ItemLoader:
    raceday = ItemLoader(item=DanishRaceday())

    raceday_info = ItemLoader(item=DanishRacedayInfo())

    raceday_info.add_value("date", raceday_json["raceDayDate"])
    raceday_info.add_value("racetrack", raceday_json["trackName"])
    raceday_info.add_value("country", "Denmark")
    raceday_info.add_value(
        "collection_date", arrow.utcnow().date().isoformat())
    raceday_info.add_value("status", "entries")

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=DanishRacedayLink())

    raceday_link.add_value("link", str(raceday_json["raceDayId"]))
    raceday_link.add_value("source", "Dansk Travsports Centralforbund")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(race_json: dict) -> ItemLoader:
    race = ItemLoader(item=DanishRace())

    race_info = ItemLoader(item=DanishRaceInfo())

    race_info.add_value("status", "entries")
    race_info.add_value("gait", "trot")
    race_info.add_value("racenumber", race_json["raceNumber"])
    race_info.add_value(
        "racetype", "qualifier" if race_json["raceType"]["code"] == "K" else "race"
    )
    race_info.add_value(
        "distance",
        [x["text"] for x in race_json["propTexts"] if x["typ"] == "T"][0],
    )
    race_info.add_value(
        "startmethod",
        [x["text"] for x in race_json["propTexts"] if x["typ"] == "T"][0],
    )
    race_info.add_value(
        "monte",
        [x["text"] for x in race_json["propTexts"] if x["typ"] == "T"][0],
    )

    if race_info.get_output_value("racetype") == "race":
        race_info.add_value(
            "purse",
            [x["text"] for x in race_json["propTexts"] if x["typ"] == "P"]
        )
        race_info.add_value(
            "racename",
            [x.get("text", "")
             for x in race_json["propTexts"] if x["typ"] == "L"],
        )
        race_info.add_value(
            "conditions",
            [x["text"]
                for x in race_json["propTexts"] if x["typ"] not in ["U", "L"]],
        )

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=DanishRaceLink())

    race_link.add_value("link", str(race_json["raceId"]))
    race_link.add_value("source", "DT")

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(starter_json: dict, race: ItemLoader) -> None:
    starter = ItemLoader(item=DanishRaceStarter())

    horse = ItemLoader(item=DanishHorse())

    horse_info = ItemLoader(item=DanishHorseInfo())

    horse_info.add_value("name", starter_json["name"])
    horse_info.add_value("country", starter_json["name"])

    horse.add_value("horse_info", horse_info.load_item())

    horse_registration = ItemLoader(item=DanishRegistration())

    horse_registration.add_value("name", starter_json["name"])
    horse_registration.add_value("link", str(starter_json["id"]))

    horse.add_value("registrations", horse_registration.load_item())

    starter.add_value("horse", horse.load_item())

    starter_info = ItemLoader(item=DanishRaceStarterInfo())

    starter_info.add_value("startnumber", starter_json["programNumber"])
    starter_info.add_value("driver", starter_json["driver"]["name"])
    starter_info.add_value("trainer", starter_json["trainer"]["name"])
    starter_info.add_value("postposition", starter_json["startPosition"])
    starter_info.add_value("distance", starter_json["actualDistance"])

    starter.add_value("starter_info", starter_info.load_item())

    race.add_value("race_starters", starter.load_item())


def parse_scratched(scratched_json: dict, race: ItemLoader) -> None:
    starter = ItemLoader(item=DanishRaceStarter())

    horse = ItemLoader(item=DanishHorse())

    horse_info = ItemLoader(item=DanishHorseInfo())

    horse_info.add_value("name", scratched_json["name"])
    horse_info.add_value("country", scratched_json["name"])

    horse.add_value("horse_info", horse_info.load_item())

    horse_registration = ItemLoader(item=DanishRegistration())

    horse_registration.add_value("name", scratched_json["name"])
    horse_registration.add_value("link", str(scratched_json["id"]))

    horse.add_value("registrations", horse_registration.load_item())

    starter.add_value("horse", horse.load_item())

    starter_info = ItemLoader(item=DanishRaceStarterInfo())

    starter_info.add_value("started", False)
    starter_info.add_value("startnumber", scratched_json["programNumber"])

    starter.add_value("starter_info", starter_info.load_item())

    race.add_value("race_starters", starter.load_item())
