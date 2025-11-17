import json

import scrapy
from scrapy.http.response import Response
from horses.items.italy import (
    ItalianHorse,
    ItalianHorseInfo,
    ItalianRace,
    ItalianRaceday,
    ItalianRacedayInfo,
    ItalianRaceInfo,
    ItalianRaceStarter,
    ItalianRaceStarterInfo,
    ItalianRaceStarterTime,
    ItalianRegistration,
    ItalianResultSummary,
)
from itemloaders import ItemLoader


def add_parents(horse: ItemLoader, sire: ItemLoader, dam: ItemLoader) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def populate_pedigree(horse: ItemLoader, ancestors: list[ItemLoader], site: str) -> None:
    if site == "unire":
        horse_parents = [
            (1, 2, 3),
            (4, 5, 6),
            (8, 9, 10),
            (11, 12, 13),
            (0, 1, 4),
            (7, 8, 11),
        ]
    else:
        horse_parents = [
            (6, 14, 15),
            (7, 16, 17),
            (8, 18, 19),
            (9, 20, 21),
            (10, 22, 23),
            (11, 24, 25),
            (12, 26, 27),
            (13, 28, 29),
            (2, 6, 7),
            (3, 8, 9),
            (4, 10, 11),
            (5, 12, 13),
            (0, 2, 3),
            (1, 4, 5),
        ]

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(ancestors[horse_index], ancestors[sire_index], ancestors[dam_index])

    add_parents(horse, ancestors[horse_parents[-2][0]], ancestors[horse_parents[-1][0]])


def parse_anact_search_result(response: Response) -> list[str]:
    res = json.loads(response.body)

    return [horse["codice"] for horse in res["data"]]


def parse_pedigree(response: Response, horse: ItemLoader) -> None:
    ancestors = []

    for rowspan in [16, 8, 4, 2]:
        for count, cell in enumerate(
            response.xpath(
                f"//table[contains(@class,'genealogy')]//td[@rowspan='{rowspan}']/div"
            )
        ):
            ancestor = ItemLoader(item=ItalianHorse())

            ancestor_info = ItemLoader(item=ItalianHorseInfo(), selector=cell)

            ancestor_info.add_value("gender", "horse" if count % 2 == 0 else "mare")

            ancestor_info.add_xpath("name", ".//a")
            ancestor_info.add_xpath("country", ".//p/span[1]")

            ancestor.add_value("horse_info", ancestor_info.load_item())

            ancestor_registration = ItemLoader(
                item=ItalianRegistration(), selector=cell
            )

            ancestor_registration.add_value("source", "anact")

            ancestor_registration.add_xpath("name", ".//a")
            ancestor_registration.add_xpath("link", ".//a/@href")
            ancestor_registration.add_xpath("registration", ".//a/@href")

            ancestor.add_value("registrations", ancestor_registration.load_item())

            for row in response.xpath(
                f"//section[contains(@id,'madre') and .//h4/a[contains(@href,'{ancestor_registration.get_output_value('link')}')]]//tbody/tr"
            ):
                offspring = ItemLoader(item=ItalianHorse())

                offspring_info = ItemLoader(item=ItalianHorseInfo(), selector=row)

                offspring.add_value("horse_info", offspring_info.load_item())

                offspring_registration = ItemLoader(
                    item=ItalianRegistration(), selector=row
                )

                offspring.add_value("registrations", offspring_registration.load_item())

                sire = ItemLoader(item=ItalianHorse())

                sire_info = ItemLoader(
                    item=ItalianHorseInfo(), selector=row.xpath("./td[5]")
                )

                sire_info.add_value("gender", "horse")

                sire_info.add_xpath("name", "./a")

                sire.add_value("horse_info", sire_info.load_item())

                sire_registration = ItemLoader(
                    item=ItalianRegistration(), selector=row.xpath("./td[5]")
                )

                sire_registration.add_value("source", "anact")

                sire_registration.add_xpath("name", "./a")
                sire_registration.add_xpath("link", "./a/@href")
                sire_registration.add_xpath("registration", "./a/@href")

                sire.add_value("registrations", sire_registration.load_item())

                offspring.add_value("sire", sire.load_item())

                ancestor.add_value("offspring", offspring.load_item())

            ancestors.append(ancestor)

    populate_pedigree(horse, ancestors, "anact")


def parse_anact_horse(response: Response, horse: ItemLoader, horse_id: str, requests: list) -> None:
    horse_info = ItemLoader(
        item=ItalianHorseInfo(), selector=response.xpath("//section[@id='info']")
    )

    horse_info.add_xpath("name", ".//h4")
    horse_info.add_xpath(
        "gender", ".//strong[text()='Sesso:']/following-sibling::text()"
    )
    horse_info.add_xpath(
        "birthdate",
        ".//strong[text()='Data di nascita:']/following-sibling::text()",
    )
    horse_info.add_xpath(
        "country", ".//strong[text()='Nazionalità:']/following-sibling::text()"
    )
    horse_info.add_xpath("breeder", ".//li/a")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=ItalianRegistration(), selector=response.xpath("//section[@id='info']")
    )

    registration.add_value("source", "anact")
    registration.add_value("registration", horse_id)
    registration.add_value("link", horse_id)

    horse.add_value("registrations", registration.load_item())

    parse_pedigree(response, horse)

    for row in response.xpath(
        "//section[@id='produzione']//table[@id='cavalli']/tbody/tr"
    ):
        offspring = ItemLoader(item=ItalianHorse())

        offspring_info = ItemLoader(item=ItalianHorseInfo(), selector=row)

        offspring_info.add_xpath("birthdate", "./td[1]")
        offspring_info.add_xpath("name", "./td[2]")
        offspring_info.add_xpath("gender", "./td[3]")

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=ItalianRegistration(), selector=row)

        offspring_registration.add_value("source", "anact")

        offspring_registration.add_xpath("name", "./td[2]")
        offspring_registration.add_xpath("link", "./td[2]/a/@href")
        offspring_registration.add_xpath("registration", "./td[2]/a/@href")

        offspring.add_value("registrations", offspring_registration.load_item())

        parent = ItemLoader(item=ItalianHorse())

        parent_info = ItemLoader(item=ItalianHorseInfo(), selector=row.xpath("./td[5]"))

        parent_info.add_value(
            "gender",
            "horse" if horse_info.get_output_value("gender") == "mare" else "mare",
        )

        parent_info.add_xpath("name", "./a")

        parent.add_value("horse_info", parent_info.load_item())

        parent_registration = ItemLoader(
            item=ItalianRegistration(), selector=row.xpath("./td[5]")
        )

        parent_registration.add_value("source", "anact")

        parent_registration.add_xpath("name", "./a")
        parent_registration.add_xpath("link", "./a/@href")
        parent_registration.add_xpath("registration", "./a/@href")

        parent.add_value("registrations", parent_registration.load_item())

        offspring.add_value(
            "sire" if horse_info.get_output_value("gender") == "mare" else "dam",
            parent.load_item(),
        )

        horse.add_value("offspring", offspring.load_item())

    if response.xpath(f"//a[contains(@href,'scheda-cavallo/?codice={horse_id}')]"):
        requests.append(
            (
                scrapy.Request,
                {"url": f"https://www.anact.it/scheda-cavallo/?codice={horse_id}"},
            )
        )


def parse_anact_starts(response: Response, horse: ItemLoader) -> None:
    result_summary = ItemLoader(
        item=ItalianResultSummary(),
        selector=response.xpath("//table[@id='statistiche']"),
    )

    result_summary.add_xpath("starts", ".//th[text()='Corse']/following-sibling::td[1]")
    result_summary.add_xpath(
        "wins", ".//th[text()='Vittorie']/following-sibling::td[1]"
    )
    result_summary.add_xpath("mark", ".//th[text()='Record']/following-sibling::td[1]")
    result_summary.add_xpath(
        "earnings", ".//th[text()='Somme']/following-sibling::td[1]"
    )

    horse.add_value("result_summaries", result_summary.load_item())

    for row in response.xpath("//table[@id='performances']/tbody/tr"):
        raceday = ItemLoader(item=ItalianRaceday())

        raceday_info = ItemLoader(item=ItalianRacedayInfo(), selector=row)

        raceday_info.add_xpath("date", "./td[1]")
        raceday_info.add_xpath("racetrack", "./td[2]")

        raceday.add_value("raceday_info", raceday_info.load_item())

        race = ItemLoader(item=ItalianRace())

        race_info = ItemLoader(item=ItalianRaceInfo(), selector=row)

        race_info.add_xpath("racenumber", "./td[3]")

        race.add_value("race_info", race_info.load_item())

        starter = ItemLoader(item=ItalianRaceStarter())

        starter_info = ItemLoader(item=ItalianRaceStarterInfo(), selector=row)

        starter_info.add_xpath("finish", "./td[4]")
        starter_info.add_xpath("purse", "./td[6]")

        starter.add_value("starter_info", starter_info.load_item())

        starter_time = ItemLoader(item=ItalianRaceStarterTime(), selector=row)

        starter_time.add_value("from_distance", 0)
        starter_time.add_value("time_format", "km")

        starter_time.add_xpath("time", "./td[5]")

        starter.add_value("times", starter_time.load_item())

        race.add_value("race_starters", starter.load_item())

        raceday.add_value("races", race.load_item())

        horse.add_value("starts", raceday.load_item())
