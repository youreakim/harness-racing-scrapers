import json

from horses.items.finland import (
    FinnishHorse,
    FinnishHorseInfo,
    FinnishRace,
    FinnishRaceday,
    FinnishRacedayInfo,
    FinnishRaceInfo,
    FinnishRaceStarter,
    FinnishRaceStarterInfo,
    FinnishRaceStarterOdds,
    FinnishRaceStarterTime,
    FinnishRegistration,
    FinnishResultSummary,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response


def add_parents(
    horse: ItemLoader | None, sire: ItemLoader | None, dam: ItemLoader | None
) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def parse_horse_info(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    horse_info = ItemLoader(item=FinnishHorseInfo())

    horse_info.add_value("name", response_json["name"])
    horse_info.add_value("birthdate", response_json["birthDate"])
    horse_info.add_value("ueln", response_json.get("ueln"))
    horse_info.add_value("chip", response_json.get("chipNo"))
    horse_info.add_value("breed", response_json["species"])
    horse_info.add_value("gender", response_json["gender"])
    horse_info.add_value("country", response_json["birthCountry"])
    horse_info.add_value("breeder", response_json["breederName"])

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=FinnishRegistration())

    registration.add_value("link", response_json["id"])
    registration.add_value("name", response_json["name"])
    registration.add_value("registration", response_json["registerNo"])
    registration.add_value("source", "Suomen Hippos")

    horse.add_value("registrations", registration.load_item())


def parse_result_summary(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for summary_json in response_json["stats"]:
        summary = ItemLoader(item=FinnishResultSummary())

        if summary_json["starts"] == "0":
            continue

        summary.add_value("year", summary_json["year"])
        summary.add_value("starts", summary_json["starts"])
        summary.add_value("wins", summary_json["firstPlaces"])
        summary.add_value("seconds", summary_json["secondPlaces"])
        summary.add_value("thirds", summary_json["thirdPlaces"])
        summary.add_value("earnings", summary_json["priceMoney"])

        horse.add_value("result_summaries", summary.load_item())


def parse_results(response: Response, horse: ItemLoader) -> bool:
    response_json = json.loads(response.body)

    for start_json in response_json:
        raceday = ItemLoader(item=FinnishRaceday())

        raceday_info = ItemLoader(item=FinnishRacedayInfo())

        raceday_info.add_value("date", start_json["date"])
        raceday_info.add_value("racetrack_code", start_json["trackCode"])

        raceday.add_value("raceday_info", raceday_info.load_item())

        race = ItemLoader(item=FinnishRace())

        race_info = ItemLoader(item=FinnishRaceInfo())

        race_info.add_value("racetype", start_json["startType"])
        race_info.add_value("racenumber", start_json["startNumber"])
        race_info.add_value("startmethod", start_json["startForm"])
        race_info.add_value("monte", start_json["monte"])

        race.add_value("race_info", race_info.load_item())

        race_starter = ItemLoader(item=FinnishRaceStarter())

        starter_info = ItemLoader(item=FinnishRaceStarterInfo())

        starter_info.add_value("distance", start_json["distance"])
        starter_info.add_value("startnumber", start_json["programNumber"])
        starter_info.add_value("postposition", start_json["lane"])
        starter_info.add_value("distance", start_json["distance"])
        starter_info.add_value("trainer", start_json.get("trainerName"))

        if start_json["driverLastName"] == "-":
            starter_info.add_value("driver", start_json["driverName"])
        else:
            starter_info.add_value(
                "driver",
                " ".join([start_json["driverFirstName"], start_json["driverLastName"]]),
            )

        starter_info.add_value("started", not start_json["absent"])

        if starter_info.get_output_value("started"):
            starter_info.add_value("finish", start_json["placing"])
            starter_info.add_value("purse", start_json["price"])
            starter_info.add_value(
                "disqualified", start_json.get("disqualifiedCode", "")
            )

            starter_time = ItemLoader(item=FinnishRaceStarterTime())

            starter_time.add_value("from_distance", 0)
            starter_time.add_value(
                "to_distance", starter_info.get_output_value("distance")
            )
            starter_time.add_value("time_format", "km")
            starter_time.add_value("time", start_json.get("kilometerTime"))

            race_starter.add_value("times", starter_time.load_item())

            if start_json["winOddsStr"] != "-":
                starter_odds = ItemLoader(item=FinnishRaceStarterOdds())

                starter_odds.add_value("odds_type", "win")
                starter_odds.add_value("odds", start_json.get("winOddsStr"))

                race_starter.add_value("odds", starter_odds.load_item())

        race_starter.add_value("starter_info", starter_info.load_item())

        race.add_value("race_starters", race_starter.load_item())

        raceday.add_value("races", race.load_item())

        horse.add_value("starts", raceday.load_item())

    return len(response_json) == 50


def parse_pedigree(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    generations = ["sire", "dam", "siresire", "siredam", "damsire", "damdam"]
    ancestors = []

    for generation in generations:
        ancestor = ItemLoader(item=FinnishHorse())

        ancestor_info = ItemLoader(item=FinnishHorseInfo())

        ancestor_info.add_value("name", response_json[generation]["name"])
        ancestor_info.add_value("birthdate", response_json[generation]["birthDate"])
        ancestor_info.add_value("ueln", response_json[generation]["ueln"])
        ancestor_info.add_value("chip", response_json[generation]["chipNo"])
        ancestor_info.add_value("breed", response_json[generation]["species"])
        ancestor_info.add_value("country", response_json[generation]["birthCountry"])
        ancestor_info.add_value("breeder", response_json[generation]["breederName"])
        ancestor_info.add_value("gender", response_json[generation]["gender"])

        ancestor.add_value("horse_info", ancestor_info.load_item())

        ancestor_registration = ItemLoader(item=FinnishRegistration())

        ancestor_registration.add_value("name", response_json[generation]["name"])
        ancestor_registration.add_value("link", response_json[generation]["id"])
        ancestor_registration.add_value(
            "registration", response_json[generation]["registerNo"]
        )

        ancestor.add_value("registrations", ancestor_registration.load_item())

        if generation in generations[2:]:
            sire = ItemLoader(item=FinnishHorse())

            sire_info = ItemLoader(item=FinnishHorseInfo())

            sire_info.add_value("gender", "horse")
            sire_info.add_value("name", response_json[generation]["sire"]["name"])

            sire.add_value("horse_info", sire_info.load_item())

            sire_registration = ItemLoader(item=FinnishRegistration())

            sire_registration.add_value(
                "name", response_json[generation]["sire"]["name"]
            )
            sire_registration.add_value("link", response_json[generation]["sire"]["id"])
            sire_registration.add_value(
                "registration", response_json[generation]["sire"]["registerNo"]
            )

            sire.add_value("registrations", sire_registration.load_item())

            ancestor.add_value("sire", sire.load_item())

            dam = ItemLoader(item=FinnishHorse())

            dam_info = ItemLoader(item=FinnishHorseInfo())

            dam_info.add_value("gender", "mare")
            dam_info.add_value("name", response_json[generation]["dam"]["name"])

            dam.add_value("horse_info", dam_info.load_item())

            dam_registration = ItemLoader(item=FinnishRegistration())

            dam_registration.add_value("name", response_json[generation]["dam"]["name"])
            dam_registration.add_value("link", response_json[generation]["dam"]["id"])
            dam_registration.add_value(
                "registration", response_json[generation]["dam"]["registerNo"]
            )

            dam.add_value("registrations", dam_registration.load_item())

            ancestor.add_value("dam", dam.load_item())

        ancestors.append(ancestor)

    add_parents(ancestors[0], ancestors[2], ancestors[3])
    add_parents(ancestors[1], ancestors[4], ancestors[5])

    add_parents(horse, ancestors[0], ancestors[1])


def parse_offspring(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for offspring_json in response_json:
        offspring = ItemLoader(item=FinnishHorse())

        offspring_info = ItemLoader(item=FinnishHorseInfo())

        offspring_info.add_value("name", offspring_json["name"])
        offspring_info.add_value("breed", offspring_json["species"])
        offspring_info.add_value("gender", offspring_json["gender"])
        offspring_info.add_value("country", offspring_json["birthCountry"])
        offspring_info.add_value("birthdate", offspring_json["birthYear"])

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=FinnishRegistration())

        offspring_registration.add_value("name", offspring_json["name"])
        offspring_registration.add_value("link", offspring_json["horseId"])

        offspring.add_value("registrations", offspring_registration.load_item())

        if offspring_json["starts"] != "0":
            summary = ItemLoader(item=FinnishResultSummary())

            summary.add_value("year", 0)
            summary.add_value("starts", offspring_json["starts"])
            summary.add_value("wins", offspring_json["firstPlaces"])
            summary.add_value("seconds", offspring_json["secondPlaces"])
            summary.add_value("thirds", offspring_json["thirdPlaces"])
            summary.add_value("earnings", offspring_json["prizeSum"])

            offspring.add_value("result_summaries", summary.load_item())

        horse.add_value("offspring", offspring.load_item())
