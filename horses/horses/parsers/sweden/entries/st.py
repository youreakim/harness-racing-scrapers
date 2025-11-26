import json
from itemloaders import ItemLoader
from scrapy.http.response import Response
from horses.items.sweden import (
    SwedishHorse,
    SwedishHorseInfo,
    SwedishRace,
    SwedishRaceday,
    SwedishRacedayInfo,
    SwedishRacedayLink,
    SwedishRaceInfo,
    SwedishRaceLink,
    SwedishRaceStarter,
    SwedishRaceStarterInfo,
    SwedishRegistration,
)


def parse_calendar(response: Response) -> list[dict]:
    response_json = json.loads(response.body)

    racedays = []

    for raceday_json in response_json:
        if not raceday_json["hasNewStartList"]:
            continue

        raceday = parse_raceday(raceday_json)

        key = f'{raceday_json["raceDayDate"]}_{raceday_json["trackName"]}'

        raceday_id = str(raceday_json["raceDayId"])

        racedays.append({"raceday": raceday, "key": key, "raceday_id": raceday_id})

    return racedays


def parse_raceday(raceday_json: dict) -> ItemLoader:
    raceday = ItemLoader(item=SwedishRaceday())

    raceday_info = ItemLoader(item=SwedishRacedayInfo())

    raceday_info.add_value("date", raceday_json["raceDayDate"])
    raceday_info.add_value("racetrack", raceday_json["trackName"])
    raceday_info.add_value("country", "Sweden")
    raceday_info.add_value("status", "startlist")

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=SwedishRacedayLink())

    raceday_link.add_value("link", str(raceday_json["raceDayId"]))
    raceday_link.add_value("source", "Svensk Travsport")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_races(response: Response, raceday: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for race_json in response_json["raceList"]:
        race = parse_race(race_json)

        for starter_json in race_json["horses"]:
            parse_starter(starter_json, race)

        raceday.add_value("races", race.load_item())


def parse_race(race_json: dict) -> ItemLoader:
    race = ItemLoader(item=SwedishRace())

    race_info = ItemLoader(item=SwedishRaceInfo())

    race_info.add_value("racenumber", race_json["raceNumber"])
    race_info.add_value("conditions", [x["text"] for x in race_json["propTexts"]])
    race_info.add_value("racetype", race_info.get_output_value("conditions"))
    race_info.add_value("monte", race_info.get_output_value("conditions"))
    race_info.add_value("startmethod", race_info.get_output_value("conditions"))
    race_info.add_value("distance", race_json["distance"])
    race_info.add_value("gait", "trot")
    race_info.add_value("status", "startlist")

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=SwedishRaceLink())

    race_link.add_value("link", race_json["raceId"])
    race_link.add_value("source", "st")

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(starter_json: dict, race: ItemLoader) -> None:
    starter = ItemLoader(item=SwedishRaceStarter())

    starter_info = ItemLoader(item=SwedishRaceStarterInfo())

    starter_info.add_value("driver", starter_json["driver"]["name"])
    starter_info.add_value("trainer", starter_json["trainer"]["name"])
    starter_info.add_value("postposition", starter_json["startPosition"])
    starter_info.add_value("distance", starter_json["actualDistance"])
    starter_info.add_value("started", not starter_json["horseWithdrawn"])
    starter_info.add_value("startnumber", starter_json["programNumberDisplay"])

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=SwedishHorse())

    horse_info = ItemLoader(item=SwedishHorseInfo())

    horse_info.add_value("name", starter_json["name"])
    horse_info.add_value("country", starter_json["name"])
    horse_info.add_value("breeder", starter_json["breeder"].get("name"))
    horse_info.add_value("gender", starter_json["horseGender"]["code"])

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=SwedishRegistration())

    registration.add_value("name", starter_json["name"])
    registration.add_value("link", starter_json["id"])

    horse.add_value("registrations", registration.load_item())

    starter.add_value("horse", horse.load_item())

    race.add_value("race_starters", starter.load_item())
