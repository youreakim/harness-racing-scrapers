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
    SwedishRaceStarterOdds,
    SwedishRaceStarterTime,
    SwedishRegistration,
    SwedishResultSummary,
)


def parse_horse_info(response: Response) -> dict:
    response_json = json.loads(response.body)

    horse_info = ItemLoader(item=SwedishHorseInfo())

    horse_info.add_value("name", response_json["name"])
    horse_info.add_value("country", response_json.get("bredCountryCode"))
    horse_info.add_value("breeder", response_json["breeder"]["name"])

    if response_json["dateOfBirthDisplayValue"] != "-":
        horse_info.add_value("birthdate", response_json["dateOfBirth"])

    horse_info.add_value("gender", response_json["horseGender"]["code"])
    horse_info.add_value("breed", response_json["horseBreed"]["code"])

    if "uelnNumber" in response_json:
        horse_info.add_value("ueln", response_json["uelnNumber"])

    registration = ItemLoader(item=SwedishRegistration())

    registration.add_value("name", response_json["name"])
    registration.add_value("link", response_json["id"])
    registration.add_value("registration", response_json["registrationNumber"])
    registration.add_value("source", "st")

    return {
        "horse_info": horse_info,
        "registration": registration,
        "offspring": response_json["offspringExists"],
        "starts": response_json["resultsExists"]
    }


def parse_pedigree(response: Response) -> tuple[ItemLoader|None, ItemLoader|None]:
    response_json = json.loads(response.body)

    return handle_pedigree(response_json)


def handle_pedigree(pedigree):
    sire, dam = None, None

    if "father" in pedigree:
        sire = ItemLoader(item=SwedishHorse())

        sire_horse_info = ItemLoader(item=SwedishHorseInfo())

        sire_horse_info.add_value("name", pedigree["father"]["name"])
        sire_horse_info.add_value("country", pedigree["father"]["name"])
        sire_horse_info.add_value("gender", "horse")

        sire_sire, sire_dam = handle_pedigree(pedigree["father"])

        if sire_sire:
            sire.add_value("sire", sire_sire.load_item())
        
        if sire_dam:
            sire.add_value("dam", sire_dam.load_item())

        sire.add_value("horse_info", sire_horse_info.load_item())

        sire_registration = ItemLoader(item=SwedishRegistration())

        sire_registration.add_value("name", pedigree["father"]["name"])
        sire_registration.add_value("link", pedigree["father"]["horseId"])
        sire_registration.add_value(
            "registration", pedigree["father"]["registrationNumber"]
        )
        sire_registration.add_value("source", "st")

        sire.add_value("registrations", sire_registration.load_item())

    if "mother" in pedigree:
        dam = ItemLoader(item=SwedishHorse())

        dam_horse_info = ItemLoader(item=SwedishHorseInfo())

        dam_horse_info.add_value("name", pedigree["mother"]["name"])
        dam_horse_info.add_value("country", pedigree["mother"]["name"])
        dam_horse_info.add_value("gender", "mare")

        dam_sire, dam_dam = handle_pedigree(pedigree["mother"])

        if dam_sire:
            dam.add_value("sire", dam_sire.load_item())

        if dam_dam:
            dam.add_value("dam", dam_dam.load_item())

        dam.add_value("horse_info", dam_horse_info.load_item())

        dam_registration = ItemLoader(item=SwedishRegistration())

        dam_registration.add_value("name", pedigree["mother"]["name"])
        dam_registration.add_value("link", pedigree["mother"]["horseId"])
        dam_registration.add_value(
            "registration", pedigree["mother"]["registrationNumber"]
        )
        dam_registration.add_value("source", "st")

        dam.add_value("registrations", dam_registration.load_item())

    return sire, dam


def parse_chip(response: Response) -> str | None:
    response_json = json.loads(response.body)

    return response_json.get("chipNumber")


def parse_offspring(response: Response, gender: str) -> list[ItemLoader]:
    response_json = json.loads(response.body)

    offspring_list = []

    for offspring in response_json["offspring"]["paginatedData"]:
        progeny = ItemLoader(item=SwedishHorse())

        if (
            offspring["numberOfStarts"]["sortValue"] is not None
            and offspring["numberOfStarts"]["sortValue"] > 0
        ):
            result_summary = ItemLoader(item=SwedishResultSummary())

            result_summary.add_value("year", 0)
            result_summary.add_value("starts", offspring["numberOfStarts"]["sortValue"])
            result_summary.add_value(
                "wins",
                offspring["firstPlaces"] if offspring["firstPlaces"] != "?" else 0,
            )
            result_summary.add_value(
                "seconds",
                offspring["secondPlaces"] if offspring["secondPlaces"] != "?" else 0,
            )
            result_summary.add_value(
                "thirds",
                offspring["thirdPlaces"] if offspring["thirdPlaces"] != "?" else 0,
            )
            result_summary.add_value("earnings", offspring["prizeMoney"]["sortValue"])

            progeny.add_value("result_summaries", result_summary.load_item())

        horse_info = ItemLoader(item=SwedishHorseInfo())

        horse_info.add_value("name", offspring["horse"]["name"])
        horse_info.add_value("country", offspring["horse"]["name"])
        horse_info.add_value("birthdate", offspring["yearBorn"])
        horse_info.add_value("gender", offspring["gender"]["code"])

        progeny.add_value("horse_info", horse_info.load_item())

        registration = ItemLoader(item=SwedishRegistration())

        registration.add_value("name", offspring["horse"]["name"])
        registration.add_value("link", offspring["horse"]["id"])
        registration.add_value("registration", offspring.get("registrationNumber"))
        registration.add_value("source", "st")

        progeny.add_value("registrations", registration.load_item())

        if offspring["horsesParent"]["id"] != 0:
            parent = ItemLoader(item=SwedishHorse())

            parent_info = ItemLoader(item=SwedishHorseInfo())

            parent_info.add_value("name", offspring["horsesParent"]["name"])
            parent_info.add_value("country", offspring["horsesParent"]["name"])
            parent_info.add_value("gender", "horse" if gender == "mare" else "mare")

            parent.add_value("horse_info", parent_info.load_item())

            parent_registration = ItemLoader(item=SwedishRegistration())

            parent_registration.add_value("name", offspring["horsesParent"]["name"])
            parent_registration.add_value("link", offspring["horsesParent"]["id"])
            parent_registration.add_value("source", "st")

            parent.add_value("registrations", parent_registration.load_item())

            if offspring["horsesParentsFather"]["id"] != 0:
                grand_parent = ItemLoader(item=SwedishHorse())

                grand_parent_info = ItemLoader(item=SwedishHorseInfo())

                grand_parent_info.add_value(
                    "name", offspring["horsesParentsFather"]["name"]
                )
                grand_parent_info.add_value(
                    "country", offspring["horsesParentsFather"]["name"]
                )
                grand_parent_info.add_value("gender", "horse")

                grand_parent.add_value("horse_info", grand_parent_info.load_item())

                grand_parent_registration = ItemLoader(item=SwedishRegistration())

                grand_parent_registration.add_value(
                    "name", offspring["horsesParentsFather"]["name"]
                )
                grand_parent_registration.add_value(
                    "link", offspring["horsesParentsFather"]["id"]
                )
                grand_parent_registration.add_value("source", "st")

                grand_parent.add_value("registrations", grand_parent_registration.load_item())

                parent.add_value("sire", grand_parent.load_item())

            progeny.add_value("dam" if gender == "horse" else "sire", parent.load_item())

        offspring_list.append(progeny)

    return offspring_list


def parse_starts(response: Response) -> list[ItemLoader]:
    response_json = json.loads(response.body)

    starts = []

    for start_json in response_json:
        raceday = ItemLoader(item=SwedishRaceday())

        raceday_info = ItemLoader(item=SwedishRacedayInfo())

        raceday_info.add_value("racetrack_code", start_json["trackCode"])
        raceday_info.add_value("date", start_json["raceInformation"]["date"])

        raceday.add_value("raceday_info", raceday_info.load_item())

        raceday_link = ItemLoader(item=SwedishRacedayLink())

        raceday_link.add_value("link", start_json["raceInformation"].get("raceDayId"))

        raceday.add_value("links", raceday_link.load_item())

        race = ItemLoader(item=SwedishRace())

        race_info = ItemLoader(item=SwedishRaceInfo())

        starter = ItemLoader(item=SwedishRaceStarter())

        if start_json["raceType"]["displayValue"] != "" and start_json["raceType"][
            "displayValue"
        ][0] in ["k", "p"]:
            race_info.add_value(
                "racetype",
                {"k": "qualifier", "p": "premium"}[
                    start_json["raceType"]["displayValue"][0]
                ],
            )
        else:
            race_info.add_value("racetype", "race")

            if start_json["odds"].get("sortValue") and start_json["odds"]["sortValue"] < 9900:
                starter_odds = ItemLoader(item=SwedishRaceStarterOdds())

                starter_odds.add_value("odds", start_json["odds"]["displayValue"])
                starter_odds.add_value("odds_type", "win")

                starter.add_value("odds", starter_odds.load_item())

        race_info.add_value(
            "racenumber", start_json["raceInformation"].get("raceNumber")
        )
        race_info.add_value(
            "startmethod",
            {"V": "standing", "A": "mobile", "L": "line", "P": "standing"}[
                start_json["startMethod"]
            ],
        )
        race_info.add_value("monte", "m" in start_json["raceType"]["displayValue"])

        race.add_value("race_info", race_info.load_item())

        race_link = ItemLoader(item=SwedishRaceLink())

        race_link.add_value("link", start_json["raceInformation"].get("raceId"))

        race.add_value("links", race_link.load_item())

        starter_info = ItemLoader(item=SwedishRaceStarterInfo())

        starter_info.add_value(
            "postposition", start_json["startPosition"].get("sortValue")
        )
        starter_info.add_value("distance", start_json["distance"].get("sortValue"))
        starter_info.add_value("finish", start_json["placement"].get("sortValue"))
        starter_info.add_value(
            "gallop", "g" in start_json["kilometerTime"].get("displayValue")
        )
        starter_info.add_value("driver", start_json["driver"].get("name"))
        starter_info.add_value("trainer", start_json["trainer"].get("name"))
        starter_info.add_value("purse", start_json["prizeMoney"].get("sortValue"))
        starter_info.add_value("started", not start_json["withdrawn"])
        starter_info.add_value(
            "disqualified", start_json["placement"].get("displayValue")#  == "d"
        )

        if start_json["kilometerTime"].get("displayValue"):
            starter_info.add_value(
                "finished", start_json["kilometerTime"]["displayValue"]# [0] == "u"
            )

        if (
            race_info.get_output_value("racetype") == "qualifier"
            and not start_json["withdrawn"]
        ):
            starter_info.add_value(
                "approved", start_json["placement"].get("displayValue")[:2] == "gdk"
            )
        elif (
            race_info.get_output_value("racetype") == "premium"
            and not start_json["withdrawn"]
        ):
            starter_info.add_value(
                "approved", start_json["placement"].get("displayValue")[0] == "p"
            )

        starter.add_value("starter_info", starter_info.load_item())

        if start_json["kilometerTime"].get("sortValue") and start_json["kilometerTime"]["sortValue"] < 9000:
            starter_time = ItemLoader(item=SwedishRaceStarterTime())

            starter_time.add_value("from_distance", 0)
            starter_time.add_value("to_distance", starter_info.get_output_value("distance"))
            starter_time.add_value("time_format", "kilometer")
            starter_time.add_value("time", start_json["kilometerTime"]["sortValue"])

            starter.add_value("times", starter_time.load_item())

        race.add_value("race_starters", starter.load_item())

        raceday.add_value("races", race.load_item())

        starts.append(raceday)

    return starts


def parse_result_summaries(response: Response) -> list[ItemLoader]:
    response_json = json.loads(response.body)

    summaries = []

    for year in response_json["statistics"]:
        if year["numberOfStarts"] == "0":
            continue

        wins, seconds, thirds = [
            int(x) if x.isnumeric() else 0 for x in year["placements"].split("-")
        ]
        earnings = int(year["prizeMoney"].replace(" ", "").replace("kr", ""))

        result_summary = ItemLoader(item=SwedishResultSummary())

        result_summary.add_value(
            "year", year["year"] if year["year"].isnumeric() else 0
        )
        result_summary.add_value("starts", year["numberOfStarts"])
        result_summary.add_value("wins", wins)
        result_summary.add_value("seconds", seconds)
        result_summary.add_value("thirds", thirds)
        result_summary.add_value("earnings", earnings)

        summaries.append(result_summary)

    return summaries
