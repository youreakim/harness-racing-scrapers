import json
from math import ceil

from horses.items.france import (
    FrenchHorse,
    FrenchHorseInfo,
    FrenchRace,
    FrenchRaceday,
    FrenchRacedayInfo,
    FrenchRacedayLink,
    FrenchRaceInfo,
    FrenchRaceLink,
    FrenchRaceStarter,
    FrenchRaceStarterInfo,
    FrenchRaceStarterTime,
    FrenchRegistration,
    FrenchResultSummary,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response


def parse_search_letrot(response: Response, name: str) -> list[str]:
    horse_ids = []

    res = json.loads(response.body)

    for horse in res["horse"]["items"]:
        if horse["NOM_CHEVAL"].startswith(name.upper()):
            horse_ids.append(horse["key"])

    return horse_ids


def get_number_starts_pages_letrot(response: Response) -> int:
    pages = 0

    res = json.loads(response.body)

    if res["total"]["races"] != 0:
        pages = ceil(res["total"]["races"] / 20)

    return pages


def get_number_offspring_pages_letrot(response: Response) -> int:
    pages = 0

    res = json.loads(response.body)

    if res["total"]["nbProduitTotal"] != 0:
        pages = ceil(res["total"]["nbProduitTotal"] / 20)

    return pages


def parse_horse_letrot(
    response: Response, horse: ItemLoader, siblings: list[dict]
) -> None:
    res = json.loads(response.body)

    if res["tree"]:
        parse_horse_info_letrot(res["tree"], horse)

        parse_pedigree_letrot(res["tree"], horse, siblings)


def parse_pedigree_letrot(
    res: dict, horse: ItemLoader, siblings: list[dict] | None = None
) -> None:
    if res.get("pere"):
        sire = ItemLoader(item=FrenchHorse())

        sire_info = ItemLoader(item=FrenchHorseInfo())

        sire_info.add_value("gender", "horse")
        sire_info.add_value("name", res["pere"]["nomch"])

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(item=FrenchRegistration())

        sire_registration.add_value("source", "letrot")
        sire_registration.add_value("name", res["pere"]["nomch"])
        sire_registration.add_value("link", res["pere"]["_id"])

        sire.add_value("registrations", sire_registration.load_item())

        parse_pedigree_letrot(res["pere"], sire)

        horse.add_value("sire", sire.load_item())

    if res.get("mere"):
        dam = ItemLoader(item=FrenchHorse())

        dam_info = ItemLoader(item=FrenchHorseInfo())

        dam_info.add_value("gender", "mare")
        dam_info.add_value("name", res["mere"]["nomch"])

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(item=FrenchRegistration())

        dam_registration.add_value("source", "letrot")
        dam_registration.add_value("name", res["mere"]["nomch"])
        dam_registration.add_value("link", res["mere"]["_id"])

        dam.add_value("registrations", dam_registration.load_item())

        if siblings is not None:
            for sibling in siblings:
                dam.add_value("offspring", sibling)

        parse_pedigree_letrot(res["mere"], dam)

        horse.add_value("dam", dam.load_item())


def parse_horse_info_letrot(res: dict, horse: ItemLoader) -> None:
    horse_info = ItemLoader(item=FrenchHorseInfo())

    horse_info.add_value("name", res["horseName"])
    horse_info.add_value("birthdate", res["birthYear"])
    horse_info.add_value("gender", res["sex"])

    if res["origin"] == "TF":
        horse_info.add_value("country", "FRA")
        horse_info.add_value("ueln", f"250001{res['horseNumber']}")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=FrenchRegistration())

    registration.add_value("source", "letrot")
    registration.add_value("name", res["horseName"])
    registration.add_value("registration", res["horseNumber"])
    registration.add_value("link", res["identifier"])

    horse.add_value("registrations", registration.load_item())


def parse_offspring_letrot(response: Response, horse: ItemLoader) -> None:
    res = json.loads(response.body)

    for progeny in res:
        offspring = ItemLoader(item=FrenchHorse())

        offspring_info = ItemLoader(item=FrenchHorseInfo())

        offspring_info.add_value("name", progeny["horseName"])
        offspring_info.add_value("birthdate", progeny["birthYear"])
        offspring_info.add_value("gender", progeny["sex"])

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_link = ItemLoader(item=FrenchRegistration())

        offspring_link.add_value("source", "letrot")
        offspring_link.add_value("name", progeny["horseName"])
        offspring_link.add_value("link", progeny["id"])

        offspring.add_value("registrations", offspring_link.load_item())

        if "horseMotherName" in progeny:
            dam = ItemLoader(item=FrenchHorse())

            dam_info = ItemLoader(item=FrenchHorseInfo())

            dam_info.add_value("gender", "mare")
            dam_info.add_value("name", progeny["horseMotherName"])
            dam_info.add_value("birthdate", progeny["birthMotherYear"])

            dam.add_value("horse_info", dam_info.load_item())

            dam_registration = ItemLoader(item=FrenchRegistration())

            dam_registration.add_value("source", "letrot")
            dam_registration.add_value("name", progeny["horseMotherName"])
            dam_registration.add_value("link", progeny["horseMotherId"])

            dam.add_value("registrations", dam_registration.load_item())

            if progeny["horseFatherMotherName"] != "":
                dam_sire = ItemLoader(item=FrenchHorse())

                dam_sire_info = ItemLoader(item=FrenchHorseInfo())

                dam_sire_info.add_value("gender", "horse")
                dam_sire_info.add_value("name", progeny["horseFatherMotherName"])

                dam_sire.add_value("horse_info", dam_sire_info.load_item())

                dam_sire_registration = ItemLoader(item=FrenchRegistration())

                dam_sire_registration.add_value("source", "letrot")
                dam_sire_registration.add_value(
                    "name", progeny["horseFatherMotherName"]
                )
                dam_sire_registration.add_value("link", progeny["horseFatherMotherId"])

                dam_sire.add_value("registrations", dam_sire_registration.load_item())

                dam.add_value("sire", dam_sire.load_item())

            offspring.add_value("dam", dam.load_item())

        elif "horseFatherName" in progeny:
            sire = ItemLoader(item=FrenchHorse())

            sire_info = ItemLoader(item=FrenchHorseInfo())

            sire_info.add_value("gender", "horse")
            sire_info.add_value("name", progeny["horseFatherName"])

            sire.add_value("horse_info", sire_info.load_item())

            sire_registration = ItemLoader(item=FrenchRegistration())

            sire_registration.add_value("source", "letrot")
            sire_registration.add_value("name", progeny["horseFatherName"])
            sire_registration.add_value("link", progeny["horseFatherId"])

            sire.add_value("registrations", sire_registration.load_item())

            offspring.add_value("sire", sire.load_item())

        horse.add_value("offspring", offspring.load_item())


def parse_result_summaries_letrot(response: Response, horse: ItemLoader) -> None:
    res = json.loads(response.body)

    for year_summary in res["data"]:
        summary = ItemLoader(item=FrenchResultSummary())

        summary.add_value("year", year_summary["id"])
        summary.add_value("starts", year_summary["numRaces"])
        summary.add_value("wins", year_summary["numVictories"])
        summary.add_value("earnings", year_summary["numGain"])
        summary.add_value("mark", year_summary["reduction"])

        horse.add_value("result_summaries", summary.load_item())

    total = ItemLoader(item=FrenchResultSummary())

    total.add_value("year", 0)
    total.add_value("starts", res["total"]["races"])
    total.add_value("wins", res["total"]["victories"])
    total.add_value("earnings", res["total"]["gains"])
    total.add_value("mark", res["total"]["reduction"])

    horse.add_value("result_summaries", total.load_item())


def parse_siblings_letrot(response: Response, siblings: list) -> None:
    res = json.loads(response.body)

    for horse in res:
        sibling = ItemLoader(item=FrenchHorse())

        sibling_info = ItemLoader(item=FrenchHorseInfo())

        sibling_info.add_value("name", horse["horseName"])
        sibling_info.add_value("birthdate", horse["birthYear"])
        sibling_info.add_value("gender", horse["sex"])

        sibling.add_value("horse_info", sibling_info.load_item())

        sibling_registration = ItemLoader(item=FrenchRegistration())

        sibling_registration.add_value("source", "letrot")
        sibling_registration.add_value("name", horse["horseName"])
        sibling_registration.add_value("link", horse["id"])
        sibling_registration.add_value("registration", horse["horseNumber"])

        sibling.add_value("registrations", sibling_registration.load_item())

        sibling_sire = ItemLoader(item=FrenchHorse())

        sibling_sire_info = ItemLoader(item=FrenchHorseInfo())

        sibling_sire_info.add_value("gender", "horse")
        sibling_sire_info.add_value("name", horse["horseFatherName"])

        sibling_sire.add_value("horse_info", sibling_sire_info.load_item())

        sibling_sire_registration = ItemLoader(item=FrenchRegistration())

        sibling_sire_registration.add_value("source", "letrot")
        sibling_sire_registration.add_value("name", horse["horseFatherName"])
        sibling_sire_registration.add_value("link", horse["horseFatherId"])
        sibling_sire_registration.add_value("registration", horse["horseFatherNumber"])

        sibling_sire.add_value("registrations", sibling_sire_registration.load_item())

        sibling.add_value("sire", sibling_sire.load_item())

        siblings.append(sibling.load_item())


def parse_starts_letrot(response: Response, horse: ItemLoader) -> None:
    res = json.loads(response.body)

    for start in res:
        raceday = ItemLoader(item=FrenchRaceday())

        raceday_info = ItemLoader(item=FrenchRacedayInfo())

        raceday_info.add_value("date", start["datePerf"])
        raceday_info.add_value("racetrack", start["nomHippodrome"])
        raceday_info.add_value("racetrack_code", start["numHippodrome"])

        raceday.add_value("raceday_info", raceday_info.load_item())

        raceday_link = ItemLoader(item=FrenchRacedayLink())

        raceday_link.add_value("source", "letrot")
        raceday_link.add_value("link", start["raceLink"])

        raceday.add_value("links", raceday_link.load_item())

        race = ItemLoader(item=FrenchRace())

        race_info = ItemLoader(item=FrenchRaceInfo())

        race_info.add_value("distance", start["distanceCourse"])
        race_info.add_value("racenumber", start["numCourse"])
        race_info.add_value("racename", start["prix"])
        race_info.add_value("monte", start["speciality"])
        race_info.add_value("purse", start["allocation"])
        race_info.add_value("startmethod", start["depart"])

        race.add_value("race_info", race_info.load_item())

        race_link = ItemLoader(item=FrenchRaceLink())

        race_link.add_value("source", "letrot")
        race_link.add_value("link", start["raceLink"])

        race.add_value("links", race_link.load_item())

        starter = ItemLoader(item=FrenchRaceStarter())

        starter_info = ItemLoader(item=FrenchRaceStarterInfo())

        starter_info.add_value("finish", start["rang"])
        starter_info.add_value("distance", start["distance"])
        starter_info.add_value("driver", start["driver"])
        starter_info.add_value("trainer", start["coach"])
        starter_info.add_value("purse", start["earnings"])

        starter.add_value("starter_info", starter_info.load_item())

        starter_time = ItemLoader(item=FrenchRaceStarterTime())

        starter_time.add_value("from_distance", 0)
        starter_time.add_value("to_distance", starter_info.get_output_value("distance"))
        starter_time.add_value("time_format", "km")
        starter_time.add_value("time", start["reduction"])

        starter.add_value("times", starter_time.load_item())

        race.add_value("race_starters", starter.load_item())

        horse.add_value("starts", race.load_item())
