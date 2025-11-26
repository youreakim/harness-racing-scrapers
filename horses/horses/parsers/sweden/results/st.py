import json
import arrow
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
    SwedishRaceStarterOdds,
    SwedishRaceStarterTime,
    SwedishRegistration,
)


def parse_st_calendar(
    response: Response,
    start_date: arrow.arrow.Arrow,
    end_date: arrow.arrow.Arrow
) -> list[dict]:
    response_json = json.loads(response.body)

    racedays = []

    for raceday_json in response_json:
        raceday_date = arrow.get(raceday_json["raceDayDate"]).date()

        if raceday_date < start_date.date() or raceday_date > end_date.date():
            continue

        raceday_info = ItemLoader(item=SwedishRacedayInfo())

        raceday_info.add_value("date", raceday_json["raceDayDate"])
        raceday_info.add_value("racetrack", raceday_json["trackName"])
        raceday_info.add_value("country", "Sweden")
        raceday_info.add_value("status", "result")
        raceday_info.add_value("collection_date", arrow.utcnow().date().isoformat())

        raceday_link = ItemLoader(item=SwedishRacedayLink())

        raceday_link.add_value("link", raceday_json["raceDayId"])
        raceday_link.add_value("source", "Svensk Travsport")

        key = f'{raceday_json["raceDayDate"]}_{raceday_json["trackName"].lower()}'

        racedays.append({
            "raceday": ItemLoader(item=SwedishRaceday()),
            "raceday_info": raceday_info,
            "raceday_link": raceday_link,
            "key": key,
            "raceday_id": raceday_json["raceDayId"]
        })

    return racedays


def parse_st_raceday(response: Response) -> list[dict]:
    response_json = json.loads(response.body)

    races = []

    for race_json in response_json["racesWithReadyResult"]:
        race = parse_st_race(race_json)

        starters = {}

        order = 1

        for order, starter_json in enumerate(race_json.get("raceResultRows", []), 1):
            starter = parse_st_starter(starter_json, order, race["race_info"].get_output_value("racetype"))

            starters[starter_json["horse"]["id"]] = starter

        for order, non_starter_json in enumerate(race_json.get("withdrawnHorses", []), order):
            non_starter = parse_st_scratched(non_starter_json, order)

            starters[non_starter_json["id"]] = non_starter

        race["starters"] = starters

        races.append(race)

    return races


def parse_st_race(race_json: dict) -> dict:
    race_info = ItemLoader(item=SwedishRaceInfo())

    race_info.add_value("racenumber", race_json["generalInfo"]["raceNumber"])
    race_info.add_value(
        "conditions", [x["text"] for x in race_json["propositionDetailRows"]]
    )
    race_info.add_value("racetype", race_info.get_output_value("conditions"))
    race_info.add_value("monte", race_info.get_output_value("conditions"))
    race_info.add_value("startmethod", race_info.get_output_value("conditions"))
    race_info.add_value(
        "distance",
        [x["text"] for x in race_json["propositionDetailRows"] if x["type"] == "T"][0],
    )
    race_info.add_value("gait", "trot")
    race_info.add_value("status", "result")
    race_info.add_value("purse", race_json["generalInfo"]["totalPriceSum"])

    race_link = ItemLoader(item=SwedishRaceLink())

    race_link.add_value("link", race_json["raceId"])
    race_link.add_value("source", "Svensk Travsport")

    return {
        "race": ItemLoader(item=SwedishRace()),
        "racenumber": race_json["generalInfo"]["raceNumber"],
        "race_info": race_info,
        "race_link": race_link,
    }


def parse_st_starter(starter_json: dict, order: int, racetype: str) -> dict:
    starter_info = ItemLoader(item=SwedishRaceStarterInfo())

    starter_info.add_value("order", order)
    starter_info.add_value("driver", starter_json["driver"]["name"])
    starter_info.add_value("trainer", starter_json["trainer"]["name"])
    starter_info.add_value("postposition", starter_json["startPositionAndDistance"])
    starter_info.add_value("distance", starter_json["startPositionAndDistance"])
    starter_info.add_value("disqualified", starter_json["time"])
    starter_info.add_value("finished", starter_json["time"])
    starter_info.add_value("gallop", starter_json["time"])
    starter_info.add_value("purse", starter_json.get("prizeMoney"))
    starter_info.add_value("started", True)
    starter_info.add_value("startnumber", starter_json["programNumber"])
    starter_info.add_value("purse", starter_json.get("prizeMoney"))

    odds = []

    if racetype == "race":
        starter_info.add_value("finish", starter_json["placementNumber"])

        if starter_json.get("odds"):
            win_odds = ItemLoader(item=SwedishRaceStarterOdds())

            win_odds.add_value("odds_type", "win")
            win_odds.add_value("odds", starter_json["odds"])

            odds.append(win_odds.load_item())

        if starter_json.get("oddsPlats"):
            show_odds = ItemLoader(item=SwedishRaceStarterOdds())

            show_odds.add_value("odds_type", "show")
            show_odds.add_value("odds", starter_json["oddsPlats"])

            odds.append(show_odds.load_item())

    else:
        starter_info.add_value("approved", starter_json["placementDisplay"])

    starter_time = None

    if "," in starter_json["time"]:
        starter_time = ItemLoader(item=SwedishRaceStarterTime())

        starter_time.add_value("from_distance", 0)
        starter_time.add_value("to_distance", starter_info.get_output_value("distance"))
        starter_time.add_value("time_format", "km")

        starter_time.add_value("time", starter_json["time"])

    horse_info = ItemLoader(item=SwedishHorseInfo())

    horse_info.add_value("name", starter_json["horse"]["name"])
    horse_info.add_value("country", starter_json["horse"]["name"])

    registration = ItemLoader(item=SwedishRegistration())

    registration.add_value("name", starter_json["horse"]["name"])
    registration.add_value("link", starter_json["horse"]["id"])
    registration.add_value("source", "st")

    return {
        "starter": ItemLoader(item=SwedishRaceStarter()),
        "horse": ItemLoader(item=SwedishHorse()),
        "starter_info": starter_info,
        "starter_time": starter_time,
        "horse_info": horse_info,
        "registration": registration,
        "odds": odds
    }


def parse_st_scratched(non_starter_json: dict, order: int) -> dict:
    starter_info = ItemLoader(item=SwedishRaceStarterInfo())

    starter_info.add_value("startnumber", non_starter_json["programNumber"])
    starter_info.add_value("started", False)
    starter_info.add_value("order", order)

    horse_info = ItemLoader(item=SwedishHorseInfo())

    horse_info.add_value("name", non_starter_json["name"])
    horse_info.add_value("country", non_starter_json["name"])

    registration = ItemLoader(item=SwedishRegistration())

    registration.add_value("name", non_starter_json["name"])
    registration.add_value("link", non_starter_json["id"])

    return {
        "starter": ItemLoader(item=SwedishRaceStarter()),
        "horse": ItemLoader(item=SwedishHorse()),
        "starter_info": starter_info,
        "starter_time": None,
        "horse_info": horse_info,
        "registration": registration,
        "odds": []
    }
