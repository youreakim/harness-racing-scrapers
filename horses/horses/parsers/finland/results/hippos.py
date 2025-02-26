import json

import arrow
from horses.items.finland import (
    FinnishHorse,
    FinnishHorseInfo,
    FinnishRace,
    FinnishRaceday,
    FinnishRacedayInfo,
    FinnishRacedayLink,
    FinnishRaceInfo,
    FinnishRaceLink,
    FinnishRaceStarter,
    FinnishRaceStarterInfo,
    FinnishRaceStarterTime,
    FinnishRegistration,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response

BASE_URL = "https://heppa.hippos.fi/heppa2_backend/race/"


def parse_races(response: Response, raceday: ItemLoader) -> list[dict]:
    response_json = json.loads(response.body)

    races = []

    for race_json in response_json:
        if race_json["race"]["startType"] == "PONI":
            continue

        race = parse_race_info(race_json)

        link = raceday.get_output_value("links")[0]["link"]
        race_number = race.get_output_value("race_info")["racenumber"]

        url = f"{BASE_URL}{link}/start/{race_number}"

        races.append(
            {
                "race": race,
                "race_number": race_number,
                "url": url,
            }
        )

    return races


def parse_race(response: Response, raceday: ItemLoader, races: dict) -> None:
    response_json = json.loads(response.body)

    racenumber = int(response_json[0]["startNumber"])

    race = races[racenumber]

    for order, starter_json in enumerate(response_json, 1):
        parse_starter(starter_json, order, race)

    raceday.add_value("races", race.load_item())


def parse_raceday_calendar(response: Response) -> list[dict]:
    response_json = json.loads(response.body)

    racedays = []

    for day_json in response_json:
        for raceday_json in day_json["events"]:
            raceday = parse_raceday(raceday_json)

            key = f"{raceday.get_output_value('raceday_info')['date']}_{raceday.get_output_value('raceday_info')['racetrack_code']}"

            url = f"{BASE_URL}{raceday.get_output_value('links')[0]['link']}/races"

            racedays.append({"raceday": raceday, "key": key, "url": url})

    return racedays


def parse_raceday(raceday_json: dict) -> ItemLoader:
    raceday = ItemLoader(item=FinnishRaceday())

    raceday_info = ItemLoader(item=FinnishRacedayInfo())

    raceday_info.add_value("date", raceday_json["date"])
    raceday_info.add_value("racetrack", raceday_json["trackShortname"])
    raceday_info.add_value("racetrack_code", raceday_json["trackCode"])
    raceday_info.add_value("status", "result")
    raceday_info.add_value("collection_date", arrow.utcnow().date().isoformat())
    raceday_info.add_value("country", "Finland")

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=FinnishRacedayLink())

    raceday_link.add_value(
        "link", f'{raceday_json["date"]}/{raceday_json["trackCode"]}'
    )
    raceday_link.add_value("source", "Suomen Hippos")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race_info(race_json: dict) -> ItemLoader:
    race = ItemLoader(item=FinnishRace())

    race_info = ItemLoader(item=FinnishRaceInfo())

    race_info.add_value("racename", race_json["race"].get("raceName"))
    race_info.add_value("racenumber", race_json["race"]["startNumber"])
    race_info.add_value("startmethod", race_json["race"]["startForm"])
    race_info.add_value("monte", race_json["race"]["monte"])
    race_info.add_value("distance", race_json["race"]["baseDistance"])
    race_info.add_value("conditions", race_json["race"]["levellingHeader"])
    race_info.add_value("purse", race_json["race"].get("priceSum", "0"))
    race_info.add_value("racetype", race_json["race"]["startType"])
    race_info.add_value("gait", "trot")
    race_info.add_value("status", "result")

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=FinnishRaceLink())

    race_link.add_value("link", race_json["race"]["startNumber"])
    race_link.add_value("source", "Suomen Hippos")

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(starter_json: dict, order: int, race: ItemLoader) -> None:
    starter = ItemLoader(item=FinnishRaceStarter())

    starter_info = ItemLoader(item=FinnishRaceStarterInfo())

    starter_info.add_value("order", order)
    starter_info.add_value("startnumber", starter_json["programNumber"])
    starter_info.add_value("postposition", starter_json["lane"])
    starter_info.add_value("distance", starter_json["distance"])
    starter_info.add_value("trainer", starter_json["trainerName"])
    starter_info.add_value(
        "driver",
        " ".join([starter_json["driverFirstName"], starter_json["driverLastName"]]),
    )

    horse = ItemLoader(item=FinnishHorse())

    horse_info = ItemLoader(item=FinnishHorseInfo())

    horse_info.add_value("name", starter_json["horseName"])
    horse_info.add_value("breed", starter_json["horseBreed"])

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=FinnishRegistration())

    registration.add_value("source", "hippos")
    registration.add_value("name", starter_json["horseName"])
    registration.add_value("link", starter_json["horseId"])

    horse.add_value("registrations", registration.load_item())

    starter.add_value("horse", horse.load_item())

    starter_info.add_value("started", not starter_json["absent"])

    if starter_info.get_output_value("started"):
        starter_info.add_value("finish", starter_json["placing"])
        starter_info.add_value("purse", starter_json["price"])
        starter_info.add_value("gallop", starter_json["gallop"])
        starter_info.add_value("disqualified", starter_json.get("disqualifiedCode", ""))

        if starter_json.get("totalTime", "0") != "0":
            starter_time = ItemLoader(item=FinnishRaceStarterTime())

            starter_time.add_value("time_format", "total")
            starter_time.add_value("from_distance", 0)
            starter_time.add_value(
                "to_distance", starter_info.get_output_value("distance")
            )
            starter_time.add_value("time", starter_json.get("totalTime"))

            starter.add_value("times", starter_time.load_item())

    starter.add_value("starter_info", starter_info.load_item())

    race.add_value("race_starters", starter.load_item())
