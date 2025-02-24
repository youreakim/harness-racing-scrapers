import json

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
    DanishResultSummary,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response


def handle_pedigree(pedigree: dict) -> tuple[ItemLoader | None, ItemLoader | None]:
    sire = ItemLoader(item=DanishHorse())
    dam = ItemLoader(item=DanishHorse())

    if "father" in pedigree:
        sire_info = ItemLoader(item=DanishHorseInfo())

        sire_info.add_value("name", pedigree["father"]["name"])
        sire_info.add_value("country", pedigree["father"]["name"])
        sire_info.add_value("gender", "horse")

        grand_sire, grand_dam = handle_pedigree(pedigree["father"])

        sire.add_value("sire", grand_sire)
        sire.add_value("dam", grand_dam)

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(item=DanishRegistration())

        sire_registration.add_value("name", pedigree["father"]["name"])
        sire_registration.add_value("link", pedigree["father"]["horseId"])
        sire_registration.add_value(
            "registration", pedigree["father"]["registrationNumber"]
        )

        sire.add_value("registrations", sire_registration.load_item())

    if "mother" in pedigree:
        dam_info = ItemLoader(item=DanishHorseInfo())

        dam_info.add_value("name", pedigree["mother"]["name"])
        dam_info.add_value("country", pedigree["mother"]["name"])
        dam_info.add_value("gender", "mare")

        grand_sire, grand_dam = handle_pedigree(pedigree["mother"])

        dam.add_value("sire", grand_sire)
        dam.add_value("dam", grand_dam)

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(item=DanishRegistration())

        dam_registration.add_value("name", pedigree["mother"]["name"])
        dam_registration.add_value("link", pedigree["mother"]["horseId"])
        dam_registration.add_value(
            "registration", pedigree["mother"]["registrationNumber"]
        )

        dam.add_value("registrations", dam_registration.load_item())

    return (
        sire.load_item() if sire.load_item() else None,
        dam.load_item() if dam.load_item() else None,
    )


def parse_horse_info(
    response: Response, horse: ItemLoader, horse_info: ItemLoader
) -> None:
    response_json = json.loads(response.body)

    registration = ItemLoader(item=DanishRegistration())

    registration.add_value("source", "Dansk Travsports Centralforbund")
    registration.add_value("name", response_json["name"])
    registration.add_value("link", response_json["id"])
    registration.add_value("registration", response_json["registrationNumber"])

    horse.add_value("registrations", registration.load_item())

    horse_info.add_value("name", response_json["name"])
    horse_info.add_value("country", response_json["name"])
    horse_info.add_value("birthdate", response_json["dateOfBirth"])
    horse_info.add_value("breed", response_json["horseBreed"])
    horse_info.add_value("breeder", response_json["breederName"])
    horse_info.add_value("gender", response_json["gender"]["text"])


def parse_horse_chip(
    response: Response, horse: ItemLoader, horse_info: ItemLoader
) -> None:
    response_json = json.loads(response.body)

    horse_info.add_value("chip", response_json.get("chipNumber"))

    horse.add_value("horse_info", horse_info.load_item())


def parse_pedigree(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    sire, dam = handle_pedigree(response_json)

    horse.add_value("sire", sire)
    horse.add_value("dam", dam)


def parse_offspring(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for offspring_json in response_json["offspring"]:
        offspring = ItemLoader(item=DanishHorse())

        offspring_info = ItemLoader(item=DanishHorseInfo())

        offspring_info.add_value("name", offspring_json["horse"]["name"])
        offspring_info.add_value("country", offspring_json["horse"]["name"])
        offspring_info.add_value("gender", offspring_json["gender"]["text"])
        offspring_info.add_value("birthdate", offspring_json["yearBorn"])

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=DanishRegistration())

        offspring_registration.add_value("link", offspring_json["horse"]["id"])
        offspring_registration.add_value("name", offspring_json["horse"]["name"])
        offspring_registration.add_value(
            "registration", offspring_json["registrationNumber"]
        )

        offspring.add_value("registrations", offspring_registration.load_item())

        parent = ItemLoader(item=DanishHorse())

        parent_info = ItemLoader(item=DanishHorseInfo())

        parent_info.add_value("name", offspring_json["horsesParent"]["name"])
        parent_info.add_value("country", offspring_json["horsesParent"]["name"])
        parent_info.add_value(
            "gender",
            (
                "horse"
                if horse.get_output_value("horse_info")["gender"] == "mare"
                else "mare"
            ),
        )

        parent.add_value("horse_info", parent_info.load_item())

        parent_registration = ItemLoader(item=DanishRegistration())

        parent_registration.add_value("name", offspring_json["horsesParent"]["name"])
        parent_registration.add_value("link", offspring_json["horsesParent"]["id"])

        parent.add_value("registrations", parent_registration.load_item())

        grand_sire = ItemLoader(item=DanishHorse())

        grand_sire_info = ItemLoader(item=DanishHorseInfo())

        grand_sire_info.add_value("name", offspring_json["horsesParentsFather"]["name"])
        grand_sire_info.add_value(
            "country", offspring_json["horsesParentsFather"]["name"]
        )
        grand_sire_info.add_value("gender", "horse")

        grand_sire.add_value("horse_info", grand_sire_info.load_item())

        grand_sire_registration = ItemLoader(item=DanishRegistration())

        grand_sire_registration.add_value(
            "name", offspring_json["horsesParentsFather"]["name"]
        )
        grand_sire_registration.add_value(
            "link", offspring_json["horsesParentsFather"]["id"]
        )

        grand_sire.add_value("registrations", grand_sire_registration.load_item())

        parent.add_value("sire", grand_sire.load_item())

        offspring.add_value(
            (
                "sire"
                if horse.get_output_value("horse_info")["gender"] == "mare"
                else "dam"
            ),
            parent.load_item(),
        )

        horse.add_value("offspring", offspring.load_item())


def parse_result_summary(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for rs_json in response_json["statistics"]:
        if rs_json["numberOfStarts"] == "0":
            continue

        result_summary = ItemLoader(item=DanishResultSummary())

        result_summary.add_value(
            "year", int(rs_json["year"]) if rs_json["year"].isnumeric() else 0
        )
        result_summary.add_value("starts", int(rs_json["numberOfStarts"]))

        wins, seconds, thirds = rs_json["placements"].split("-")

        result_summary.add_value("wins", int(wins))
        result_summary.add_value("seconds", int(seconds))
        result_summary.add_value("thirds", int(thirds))

        result_summary.add_value("earnings", rs_json["prizeMoney"])
        result_summary.add_value("mark", rs_json["mark"])

        horse.add_value("result_summaries", result_summary.load_item())


def parse_results(response: Response, horse: ItemLoader) -> None:
    response_json = json.loads(response.body)

    for raceline in response_json:
        raceday = ItemLoader(item=DanishRaceday())

        raceday_info = ItemLoader(item=DanishRacedayInfo())

        raceday_info.add_value("racetrack_code", raceline["trackCode"])
        raceday_info.add_value(
            "country", "Denmark" if raceline["raceInformation"]["linkable"] else None
        )
        raceday_info.add_value("date", raceline["raceInformation"]["date"])

        raceday.add_value("raceday_info", raceday_info.load_item())

        raceday_link = ItemLoader(item=DanishRacedayLink())

        raceday_link.add_value("link", raceline["raceInformation"]["raceDayId"])
        raceday_link.add_value(
            "source",
            (
                "Dansk Travsports Centralforbund"
                if raceline["raceInformation"]["linkable"]
                else None
            ),
        )
        raceday.add_value("links", raceday_link.load_item())

        race = ItemLoader(item=DanishRace())

        race_link = ItemLoader(item=DanishRaceLink())

        race_link.add_value("link", raceline["raceInformation"]["raceId"])

        race.add_value("links", race_link.load_item())

        race_info = ItemLoader(item=DanishRaceInfo())

        race_info.add_value("racenumber", raceline["raceInformation"]["raceNumber"])
        race_info.add_value("startmethod", raceline["startMethod"])
        race_info.add_value("racetype", raceline["raceType"]["displayValue"])

        if race_info.get_output_value("startmethod") == "mobile":
            race_info.add_value("distance", raceline["distance"]["sortValue"])

        race.add_value("race_info", race_info.load_item())

        starter = ItemLoader(item=DanishRaceStarter())

        starter_info = ItemLoader(item=DanishRaceStarterInfo())

        starter_info.add_value(
            "postposition", raceline["startPosition"]["displayValue"]
        )
        starter_info.add_value("distance", raceline["distance"]["sortValue"])
        starter_info.add_value("started", not raceline["withdrawn"])

        if starter_info.get_output_value("started"):
            starter_info.add_value("finish", raceline["placement"]["displayValue"])
            starter_info.add_value("gallop", raceline["kilometerTime"]["displayValue"])
            starter_info.add_value(
                "finished", raceline["kilometerTime"]["displayValue"]
            )
            starter_info.add_value("driver", raceline["driver"]["name"])
            starter_info.add_value(
                "disqualified", raceline["placement"]["displayValue"]
            )

            starter_time = ItemLoader(item=DanishRaceStarterTime())

            starter_time.add_value("from_distance", 0)
            starter_time.add_value("to_distance", raceline["distance"]["sortValue"])
            starter_time.add_value("time_format", "km")
            starter_time.add_value("time", raceline["kilometerTime"]["sortValue"])

            starter.add_value("times", starter_time.load_item())

            if race_info.get_output_value("racetype") == "qualifier":
                starter_info.add_value("approved", raceline["odds"]["displayValue"])
            else:
                starter_info.add_value("purse", raceline["prizeMoney"]["displayValue"])

                starter_odds = ItemLoader(item=DanishRaceStarterOdds())

                starter_odds.add_value("odds_type", "win")
                starter_odds.add_value("odds", raceline["odds"]["sortValue"])

                starter.add_value("odds", starter_odds.load_item())

        starter.add_value("starter_info", starter_info.load_item())

        race.add_value("race_starters", starter.load_item())

        raceday.add_value("races", race.load_item())

        horse.add_value("starts", raceday.load_item())
