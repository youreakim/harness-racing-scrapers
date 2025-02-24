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
    DanishRaceStarterOdds,
    DanishRaceStarterTime,
    DanishRegistration,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response


def parse_calendar(response: Response) -> list[dict]:
    response_json = json.loads(response.body)

    racedays = []

    for raceday_json in response_json:
        raceday = parse_raceday(raceday_json)

        url = f"https://api.danskhv.dk/webapi/trot/raceinfo/{raceday.get_output_value('links')[0]['link']}/results"

        key = f"{raceday.get_output_value('raceday_info')['date']}_{raceday.get_output_value('raceday_info')['racetrack']}"

        racedays.append({"raceday": raceday, "url": url, "key": key})

    return racedays


def parse_races(response: Response, raceday: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for race_json in response_json["racesWithReadyResult"]:
        race = parse_race(race_json)

        order = 1

        for order, starter_json in enumerate(
            race_json.get("raceResultRows", []), order
        ):
            parse_starter(
                starter_json,
                order,
                race,
                raceday,
                race_json.get("winnerHorses", []),
            )

        for scratch_order, scratched_json in enumerate(
            race_json.get("withdrawnHorses", []), order + 1
        ):
            parse_scratched(scratched_json, scratch_order, race)

        raceday.add_value("races", race.load_item())


def parse_raceday(raceday_json: dict) -> ItemLoader:
    raceday = ItemLoader(item=DanishRaceday())

    raceday_info = ItemLoader(item=DanishRacedayInfo())

    raceday_info.add_value("date", raceday_json["raceDayDate"])
    raceday_info.add_value("racetrack", raceday_json["trackName"])
    raceday_info.add_value("country", "Denmark")
    raceday_info.add_value("collection_date", arrow.utcnow().date().isoformat())
    raceday_info.add_value("status", "result")

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=DanishRacedayLink())

    raceday_link.add_value("link", str(raceday_json["raceDayId"]))
    raceday_link.add_value("source", "Dansk Travsports Centralforbund")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(race_json: dict) -> ItemLoader:
    race = ItemLoader(item=DanishRace())

    race_info = ItemLoader(item=DanishRaceInfo())

    race_info.add_value("status", "result")
    race_info.add_value("gait", "trot")
    race_info.add_value("racenumber", race_json["generalInfo"]["raceNumber"])
    race_info.add_value(
        "racetype",
        " ".join(
            x["text"] for x in race_json["propositionDetailRows"] if x["type"] == "L"
        ),
    )
    race_info.add_value(
        "distance",
        [x["text"] for x in race_json["propositionDetailRows"] if x["type"] == "T"][0],
    )
    race_info.add_value(
        "startmethod",
        [x["text"] for x in race_json["propositionDetailRows"] if x["type"] == "T"][0],
    )
    race_info.add_value(
        "monte",
        [x["text"] for x in race_json["propositionDetailRows"] if x["type"] == "T"][0],
    )

    if race_info.get_output_value("racetype") == "race":
        race_info.add_value(
            "purse",
            [x["text"] for x in race_json["propositionDetailRows"] if x["type"] == "P"][
                0
            ],
        )
        race_info.add_value(
            "racename",
            [x["text"] for x in race_json["propositionDetailRows"] if x["type"] == "L"],
        )
        race_info.add_value(
            "conditions",
            [
                x["text"]
                for x in race_json["propositionDetailRows"]
                if x["type"] not in ["U", "L"]
            ],
        )

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=DanishRaceLink())

    race_link.add_value("link", str(race_json["raceId"]))
    race_link.add_value("source", "DT")

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(
    starter_json: dict,
    order: int,
    race: ItemLoader,
    raceday: ItemLoader,
    pedigrees: dict,
) -> None:
    starter = ItemLoader(item=DanishRaceStarter())

    horse = ItemLoader(item=DanishHorse())

    horse_info = ItemLoader(item=DanishHorseInfo())

    horse_info.add_value("name", starter_json["horse"]["name"])
    horse_info.add_value("country", starter_json["horse"]["name"])

    if (
        race.get_output_value("race_info")["racetype"] == "race"
        and starter_json["placementDisplay"] == "1"
    ):
        for horse_json in pedigrees:
            if horse_json["id"] == starter_json["horse"]["id"]:
                parse_pedigree(horse_json, horse, horse_info, raceday)

                break

    horse.add_value("horse_info", horse_info.load_item())

    horse_registration = ItemLoader(item=DanishRegistration())

    horse_registration.add_value("name", starter_json["horse"]["name"])
    horse_registration.add_value("link", str(starter_json["horse"]["id"]))

    horse.add_value("registrations", horse_registration.load_item())

    starter.add_value("horse", horse.load_item())

    starter_info = ItemLoader(item=DanishRaceStarterInfo())

    starter_info.add_value("order", order)
    starter_info.add_value("started", True)
    starter_info.add_value("finish", starter_json["placementDisplay"])
    starter_info.add_value("startnumber", starter_json["programNumber"])
    starter_info.add_value("driver", starter_json["driver"]["name"])
    starter_info.add_value("trainer", starter_json["trainer"]["name"])
    starter_info.add_value(
        "postposition",
        starter_json["startPositionAndDistance"].split("/")[0],
    )
    starter_info.add_value(
        "distance", starter_json["startPositionAndDistance"].split("/")[1]
    )
    starter_info.add_value("gallop", starter_json["time"])
    starter_info.add_value("finished", starter_json["time"])
    starter_info.add_value("disqualified", starter_json["placementDisplay"])

    starter_time = ItemLoader(item=DanishRaceStarterTime())

    starter_time.add_value("time", starter_json["time"])
    starter_time.add_value("time_format", "total")
    starter_time.add_value("from_distance", 0)
    starter_time.add_value("to_distance", starter_info.get_output_value("distance"))

    starter.add_value("times", starter_time.load_item())

    # if starter_info.get_output_value('disqualified'):
    #     starter_info.add_value('dq_code', starter_json['time'])

    if race.get_output_value("race_info")["racetype"] == "race":
        for odds_type in ["win", "show"]:
            starter_odds = ItemLoader(item=DanishRaceStarterOdds())

            starter_odds.add_value("odds_type", odds_type)

            odds = starter_json.get("odds" + "" if odds_type == "win" else "Plats")

            if odds:
                starter_odds.add_value("odds", odds)

                starter.add_value("odds", starter_odds.load_item())

        # starter_info.add_value('win_odds', starter_json['odds'])
        # starter_info.add_value('show_odds', starter_json.get('oddsPlats'))
        starter_info.add_value("purse", starter_json.get("prizeMoney", 0))

    else:
        starter_info.add_value("approved", starter_json["placementDisplay"])

    starter.add_value("starter_info", starter_info.load_item())

    race.add_value("race_starters", starter.load_item())


def parse_scratched(scratched_json: dict, order: int, race: ItemLoader) -> None:
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

    starter_info.add_value("order", order)
    starter_info.add_value("started", False)
    starter_info.add_value("startnumber", scratched_json["programNumber"])

    starter.add_value("starter_info", starter_info.load_item())

    race.add_value("race_starters", starter.load_item())


def parse_pedigree(
    horse_json: dict, horse: ItemLoader, horse_info: ItemLoader, raceday: ItemLoader
) -> None:
    horse_info.add_value("gender", horse_json["colorAndGenderCode"])
    horse_info.add_value(
        "birthdate",
        int(raceday.get_output_value("raceday_info")["date"][:4]) - horse_json["age"],
    )
    horse_info.add_value("breeder", horse_json["breeder"]["name"])

    sire = ItemLoader(item=DanishHorse())

    sire_info = ItemLoader(item=DanishHorseInfo())

    sire_info.add_value("gender", "horse")
    sire_info.add_value("name", horse_json["father"]["name"])
    sire_info.add_value("country", horse_json["father"]["name"])

    sire.add_value("horse_info", sire_info.load_item())

    sire_registration = ItemLoader(item=DanishRegistration())

    sire_registration.add_value("name", horse_json["father"]["name"])
    sire_registration.add_value("link", str(horse_json["father"]["id"]))

    sire.add_value("registrations", sire_registration.load_item())

    horse.add_value("sire", sire.load_item())

    dam = ItemLoader(item=DanishHorse())

    dam_info = ItemLoader(item=DanishHorseInfo())

    dam_info.add_value("gender", "mare")
    dam_info.add_value("name", horse_json["mother"]["name"])
    dam_info.add_value("country", horse_json["mother"]["name"])

    dam.add_value("horse_info", dam_info.load_item())

    dam_registration = ItemLoader(item=DanishRegistration())

    dam_registration.add_value("name", horse_json["mother"]["name"])
    dam_registration.add_value("link", str(horse_json["mother"]["id"]))

    dam.add_value("registrations", dam_registration.load_item())

    dam_sire = ItemLoader(item=DanishHorse())

    dam_sire_info = ItemLoader(item=DanishHorseInfo())

    dam_sire_info.add_value("gender", "horse")
    dam_sire_info.add_value("name", horse_json["mothersFather"]["name"])
    dam_sire_info.add_value("country", horse_json["mothersFather"]["name"])

    dam_sire.add_value("horse_info", dam_sire_info.load_item())

    dam_sire_registration = ItemLoader(item=DanishRegistration())

    dam_sire_registration.add_value("name", horse_json["mothersFather"]["name"])
    dam_sire_registration.add_value("link", str(horse_json["mothersFather"]["id"]))

    dam_sire.add_value("registrations", dam_sire_registration.load_item())

    dam.add_value("sire", dam_sire.load_item())

    horse.add_value("dam", dam.load_item())
