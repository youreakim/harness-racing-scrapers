import json
from itemloaders import ItemLoader
from scrapy.http.response import Response
from horses.items.sweden import (
    SwedishHorse,
    SwedishHorseInfo,
    SwedishRace,
    SwedishRaceInfo,
    SwedishRaceLink,
    SwedishRaceStarter,
    SwedishRaceStarterInfo,
    SwedishRaceStarterTime,
    SwedishRaceday,
    SwedishRacedayInfo,
    SwedishRacedayLink,
    SwedishRaceStarterOdds,
    SwedishRegistration,
)


def parse_atg_calendar(response: Response) -> list[dict]:
    calendar_json = json.loads(response.body)

    racedays = []

    for raceday_json in calendar_json["tracks"]:
        if raceday_json["countryCode"] == "SE" and raceday_json["sport"] == "trot":
            key = f'{calendar_json["date"]}_{raceday_json["name"].lower()}'
            races = len(raceday_json["races"])
            racetrack_id = raceday_json["id"]

            raceday = ItemLoader(item=SwedishRaceday())

            raceday_info = ItemLoader(item=SwedishRacedayInfo())

            raceday_info.add_value("date", calendar_json["date"])
            raceday_info.add_value("racetrack", raceday_json["name"])
            raceday_info.add_value("status", "results")

            raceday.add_value("raceday_info", raceday_info.load_item())

            raceday_link = ItemLoader(item=SwedishRacedayLink())

            raceday_link.add_value("link", raceday_json["races"][0]["id"])
            raceday_link.add_value("source", "atg")

            raceday.add_value("links", raceday_link.load_item())

            racedays.append({
                "raceday": raceday,
                "key": key,
                "racetrack_id": racetrack_id,
                "races": races,
                "date": calendar_json["date"]
            })

    return racedays


def parse_atg_race(response: Response) -> dict:
    response_json = json.loads(response.body)

    race_json = response_json["races"][0]

    race_info = ItemLoader(item=SwedishRaceInfo())

    race_info.add_value("racenumber", race_json["number"])
    race_info.add_value("distance", race_json["distance"])
    race_info.add_value("startmethod", race_json["startMethod"])
    race_info.add_value("conditions", "".join([*race_json["terms"], race_json["prize"]]))
    race_info.add_value("gait", race_json["sport"])
    race_info.add_value("racename", race_json.get("name"))
    race_info.add_value("monte", race_info.get_output_value("conditions"))
    race_info.add_value("purse", race_json["prize"])

    race_link = ItemLoader(item=SwedishRaceLink())

    race_link.add_value("link", response.url)
    race_link.add_value("source", "atg")

    odds = {startnumber: [] for startnumber in range(1,len(race_json["starts"]) + 1)}

    if "plats" in race_json["pools"]:
        for winner_json in race_json["pools"]["plats"]["result"]["winners"].values():
            for odds_json in winner_json:
                o = ItemLoader(item=SwedishRaceStarterOdds())

                o.add_value("odds", odds_json["odds"] / 100)
                o.add_value("odds_type", "show")

                odds[odds_json["number"]].append(o.load_item())

    starters = {}

    for starter_json in race_json["starts"]:
        starter_info = ItemLoader(item=SwedishRaceStarterInfo())

        starter_info.add_value("startnumber", starter_json["number"])
        starter_info.add_value("postposition", starter_json["postPosition"])
        starter_info.add_value("distance", starter_json["distance"])
        starter_info.add_value("order", starter_json["result"]["finishOrder"])
        starter_info.add_value("started", "scratched" not in starter_json)
        starter_info.add_value(
            "driver",
            f'{starter_json["driver"]["firstName"]} {starter_json["driver"]["lastName"]}'
        )
        starter_info.add_value(
            "trainer",
            f'{starter_json["horse"]["trainer"]["firstName"]} {starter_json["horse"]["trainer"]["lastName"]}'
        )

        starter_time = None

        if "scratched" not in starter_json:
            starter_info.add_value("finish", starter_json["result"].get("place"))
            starter_info.add_value("purse", starter_json["result"]["prizeMoney"])
            starter_info.add_value("disqualified", "disqualified" in starter_json["result"])
            starter_info.add_value("gallop", "galopped" in starter_json["result"])
            starter_info.add_value("finished", "out" not in starter_json)

            if "kmTime" in starter_json["result"]:
                t = starter_json["result"]["kmTime"]

                if "code" not in t:
                    starter_time = ItemLoader(item=SwedishRaceStarterTime())

                    starter_time.add_value("from_distance", 0)
                    starter_time.add_value("to_distance", starter_json["distance"])
                    starter_time.add_value("time_format", "kilometer")
                    starter_time.add_value(
                        "time",
                        t["minutes"] * 60 + float(f"{t["seconds"]}.{t["tenths"]}")
                    )

            starter_odds = ItemLoader(item=SwedishRaceStarterOdds())

            starter_odds.add_value("odds", starter_json["pools"]["vinnare"]["odds"] / 100)
            starter_odds.add_value("odds_type", "win")

            odds[starter_json["number"]].append(starter_odds.load_item())

        horse_info = ItemLoader(item=SwedishHorseInfo())

        horse_info.add_value("name", starter_json["horse"]["name"])
        horse_info.add_value("gender", starter_json["horse"]["sex"])
        horse_info.add_value("birthdate", str(int(race_json["date"][:4]) - starter_json["horse"]["age"]))
        horse_info.add_value("breeder", starter_json["horse"]["breeder"]["name"])
        horse_info.add_value("country", starter_json["horse"].get("nationality", "SE"))

        registration = ItemLoader(item=SwedishRegistration())

        registration.add_value("name", starter_json["horse"]["name"])
        registration.add_value("link", str(starter_json["horse"]["id"]))
        registration.add_value("source", "st")

        sire, dam = parse_atg_pedigree(starter_json["horse"]["pedigree"])

        starters[starter_json["horse"]["id"]] = {
            "starter": ItemLoader(item=SwedishRaceStarter()),
            "starter_info": starter_info,
            "starter_time": starter_time,
            "horse": ItemLoader(item=SwedishHorse()),
            "horse_info": horse_info,
            "registration": registration,
            "sire": sire,
            "dam": dam,
            "odds": odds[starter_json["number"]]
        }

    return {
        "race": ItemLoader(item=SwedishRace()),
        "racenumber": race_json["number"],
        "race_info": race_info,
        "race_link": race_link,
        "starters": starters
    }


def parse_atg_pedigree(pedigree_json: dict) -> tuple[ItemLoader, ItemLoader]:
    sire = ItemLoader(item=SwedishHorse())

    sire_horse_info = ItemLoader(item=SwedishHorseInfo())

    sire_horse_info.add_value(
        "name", pedigree_json["father"]["name"]
    )
    sire_horse_info.add_value("gender", "horse")
    sire_horse_info.add_value(
        "country",
        pedigree_json["father"].get("nationality", "SE"),
    )

    sire.add_value("horse_info", sire_horse_info.load_item())

    sire_registration = ItemLoader(item=SwedishRegistration())

    sire_registration.add_value("source", "st")
    sire_registration.add_value(
        "name", pedigree_json["father"]["name"]
    )
    sire_registration.add_value(
        "link", pedigree_json["father"]["id"]
    )

    sire.add_value("registrations", sire_registration.load_item())

    dam = ItemLoader(item=SwedishHorse())

    dam_horse_info = ItemLoader(item=SwedishHorseInfo())

    dam_horse_info.add_value(
        "name", pedigree_json["mother"]["name"]
    )
    dam_horse_info.add_value("gender", "mare")
    dam_horse_info.add_value(
        "country",
        pedigree_json["mother"].get("nationality", "SE"),
    )

    dam.add_value("horse_info", dam_horse_info.load_item())

    dam_registration = ItemLoader(item=SwedishRegistration())

    dam_registration.add_value("source", "st")
    dam_registration.add_value(
        "name", pedigree_json["mother"]["name"]
    )
    dam_registration.add_value(
        "link", pedigree_json["mother"]["id"]
    )

    dam.add_value("registrations", dam_registration.load_item())

    dam_sire = ItemLoader(item=SwedishHorse())

    dam_sire_horse_info = ItemLoader(item=SwedishHorseInfo())

    dam_sire_horse_info.add_value(
        "name", pedigree_json["grandfather"]["name"]
    )
    dam_sire_horse_info.add_value("gender", "horse")
    dam_sire_horse_info.add_value(
        "country",
        pedigree_json["grandfather"].get("nationality", "SE"),
    )

    dam_sire.add_value("horse_info", dam_sire_horse_info.load_item())

    dam_sire_registration = ItemLoader(item=SwedishRegistration())

    dam_sire_registration.add_value("source", "st")
    dam_sire_registration.add_value(
        "name", pedigree_json["grandfather"]["name"]
    )
    dam_sire_registration.add_value(
        "link", pedigree_json["grandfather"]["id"]
    )

    dam_sire.add_value("registrations", dam_sire_registration.load_item())

    dam.add_value("sire", dam_sire.load_item())

    return sire, dam
