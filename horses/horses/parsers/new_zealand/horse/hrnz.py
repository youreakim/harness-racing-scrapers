from parsel import Selector
from scrapy.http.response import Response
from horses.items.new_zealand import (
    NZHorse,
    NZHorseInfo,
    NZRace,
    NZRaceday,
    NZRacedayInfo,
    NZRacedayLink,
    NZRaceInfo,
    NZRaceLink,
    NZRaceStarter,
    NZRaceStarterInfo,
    NZRegistration,
    NZResultSummary,
)
from itemloaders import ItemLoader


def handle_cell(cell: Selector, count: int) -> ItemLoader | None:
    if not cell.xpath("./a"):
        return None

    horse = ItemLoader(item=NZHorse())

    horse_info = ItemLoader(item=NZHorseInfo(), selector=cell)

    horse_info.add_value(
        "gender",
        (
            "horse"
            if count in [0, 1, 2, 3, 6, 9, 10, 13, 16, 17, 18, 21, 24, 25, 28]
            else "mare"
        ),
    )

    horse_info.add_xpath("name", "./a")
    horse_info.add_xpath("country", './a[contains(text(),"(")]')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=NZRegistration(), selector=cell)

    registration.add_value("source", "hrnz")

    registration.add_xpath("name", "./a")
    registration.add_xpath("link", "./a/@href")

    horse.add_value("registrations", registration.load_item())

    return horse


def add_parents(horse: ItemLoader | None, sire: ItemLoader | None, dam: ItemLoader | None) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def populate_pedigree(horse: ItemLoader, ancestors: list[ItemLoader | None]) -> None:
    horse_parents = [
        (2, 3, 4),
        (5, 6, 7),
        (9, 10, 11),
        (12, 13, 14),
        (17, 18, 19),
        (20, 21, 22),
        (24, 25, 26),
        (27, 28, 29),
        (1, 2, 5),
        (8, 9, 12),
        (16, 17, 20),
        (23, 24, 27),
        (0, 1, 8),
        (15, 16, 23),
    ]

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(ancestors[horse_index], ancestors[sire_index], ancestors[dam_index])

    add_parents(horse, ancestors[0], ancestors[15])


def parse_horse_info(response: Response, horse: ItemLoader | None = None) -> ItemLoader | None:
    return_horse = not isinstance(horse, NZHorse)

    horse = horse or ItemLoader(item=NZHorse())

    horse_info = ItemLoader(
        item=NZHorseInfo(),
        selector=response.xpath('//div[contains(@class,"hrnz-block--padding")]')
    )

    horse_info.add_xpath("name", ".//h1")
    horse_info.add_xpath(
        "gender",
        ".//h5/text()[1]",
    )
    horse_info.add_xpath("chip", './/dt[text()="Microchip"]/following-sibling::dd[1]')
    horse_info.add_xpath(
        "birthdate", './/dt[text()="Foal Date"]/following-sibling::dd[1]'
    )
    horse_info.add_xpath("breeder", './/dt[text()="Breeder"]/following-sibling::dd[1]')
    horse_info.add_xpath("country", './/dt[text()="Origin"]/following-sibling::dd[1]')

    horse_info.add_value("breed", "standardbred")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=NZRegistration(),
        selector=response.xpath('//div[contains(@class,"hrnz-block--padding")]')
    )

    registration.add_value("source", "hrnz")

    registration.add_xpath("name", ".//h1")
    registration.add_xpath("link", ".//h1/a/@href")

    horse.add_value("registrations", registration.load_item())

    for summary_row in response.xpath(
        '//div[@class="hrnz-horse__racing-statistics"]//tbody/tr[count(td)>1]'
    ):
        summary = ItemLoader(item=NZResultSummary(), selector=summary_row)

        summary.add_xpath("year", "./td[1]")
        summary.add_xpath("starts", "./td[3]")
        summary.add_xpath("wins", "./td[4]")
        summary.add_xpath("seconds", "./td[5]")
        summary.add_xpath("thirds", "./td[6]")
        summary.add_xpath("earnings", "./td[7]")

        horse.add_value("result_summaries", summary.load_item())

    return horse if return_horse else None


def parse_pedigree(response: Response, horse: ItemLoader) -> None:
    ancestors = [
        handle_cell(cell, count)
        for count, cell in enumerate(
            response.xpath('//div[@class="hrnz-pedigree__entry"]/span')
        )
    ]

    populate_pedigree(horse, ancestors)


def parse_starts(response: Response, horse: ItemLoader) -> None:
    for start_row in response.xpath("//div[@data-type='premier']"):
        raceday = ItemLoader(item=NZRaceday())

        raceday_info = ItemLoader(item=NZRacedayInfo(), selector=start_row)

        raceday_info.add_xpath("date", './/div[@class="hrnz-results__date"]')
        raceday_info.add_xpath("racetrack", './/div[@class="hrnz-results__club"]/a')

        raceday.add_value("raceday_info", raceday_info.load_item())

        race = ItemLoader(item=NZRace(), selector=start_row)

        race_info = ItemLoader(item=NZRaceInfo(), selector=start_row)

        race_info.add_xpath("conditions", './/dl[@class="hrnz-results__race-type"]/dd')
        race_info.add_xpath(
            "distance",
            'substring-before(.//dl[@class="hrnz-results__distance"]/dd/text(),"m")',
        )
        race_info.add_xpath(
            "startmethod",
            'substring-before(.//dl[@class="hrnz-results__start"]/dd/text()," (")',
        )
        race_info.add_xpath("purse", './/dl[@class="hrnz-results__stake"]/dd')

        race_info.add_value("racetype", "race")

        race.add_value("race_info", race_info.load_item())

        race_link = ItemLoader(item=NZRaceLink(), selector=start_row)

        race_link.add_value("source", "hrnz")

        race_link.add_xpath("link", './/div[@class="hrnz-results__club"]/a/@href')

        race_starter = ItemLoader(item=NZRaceStarter())

        starter_info = ItemLoader(item=NZRaceStarterInfo(), selector=start_row)

        starter_info.add_xpath("finish", './/div[@class="hrnz-results__place"]')
        starter_info.add_xpath("driver", './/dl[@class="hrnz-results__driver"]/dd')
        starter_info.add_xpath("trainer", './/dl[@class="hrnz-results__trainer"]/dd')
        starter_info.add_xpath("purse", './/dl[@class="hrnz-results__won"]/dd')

        if starter_info.get_output_value("finish") == 1:
            starter_info.add_xpath(
                "racetime",
                'substring-before(.//dl[@class="hrnz-results__time"]/dd/text()," (")',
            )

        race_starter.add_value("starter_info", starter_info.load_item())

        race.add_value("race_starters", race_starter.load_item())

        race.add_value("links", race_link.load_item())

        raceday.add_value("races", race.load_item())

        horse.add_value("starts", raceday.load_item())


def parse_sire_offspring(response: Response, horse: ItemLoader) -> None:
    for offspring_row in response.xpath(
        '//table//tr[td[1]/a[not(text()="Unregistered") and not(text()="Unnamed") and string-length(text())>0]]'
    ):
        offspring = ItemLoader(item=NZHorse())

        offspring_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        # offspring_info.add_xpath('birthdate', './td[1]')
        offspring_info.add_xpath("gender", "./td[4]")
        offspring_info.add_xpath("name", "./td[1]/a")

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(
            item=NZRegistration(), selector=offspring_row
        )

        offspring_registration.add_value("source", "hrnz")

        offspring_registration.add_xpath("name", "./td[1]/a")
        offspring_registration.add_xpath("link", "./td[1]/a/@href")

        offspring.add_value("registrations", offspring_registration.load_item())

        dam = ItemLoader(item=NZHorse())

        dam_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        dam_info.add_value("gender", "mare")

        dam_info.add_xpath("name", "./td[6]/a")

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(item=NZRegistration(), selector=offspring_row)

        dam_registration.add_value("source", "hrnz")

        dam_registration.add_xpath("name", "./td[6]/a")
        dam_registration.add_xpath("link", "./td[6]/a/@href")

        dam.add_value("registrations", dam_registration.load_item())

        dam_sire = ItemLoader(item=NZHorse())

        dam_sire_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        dam_sire_info.add_value("gender", "horse")

        dam_sire_info.add_xpath("name", "./td[7]/a")

        dam_sire.add_value("horse_info", dam_sire_info.load_item())

        dam_sire_registration = ItemLoader(
            item=NZRegistration(), selector=offspring_row
        )

        dam_sire_registration.add_value("source", "hrnz")

        dam_sire_registration.add_xpath("name", "./td[7]/a")
        dam_sire_registration.add_xpath("link", "./td[7]/a/@href")

        dam_sire.add_value("registrations", dam_sire_registration.load_item())

        dam.add_value("sire", dam_sire.load_item())

        offspring.add_value("dam", dam.load_item())

        horse.add_value("offspring", offspring.load_item())


def parse_dam_offspring(response: Response, horse: ItemLoader) -> None:
    for offspring_row in response.xpath(
        "//table//tr[td[4]/a[not(text()='Unregistered') and not(text()='Unnamed') and string-length(text())>0]]"
    ):
        offspring = ItemLoader(item=NZHorse())

        offspring_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        offspring_info.add_xpath("birthdate", "./td[1]")
        offspring_info.add_xpath("gender", "./td[3]")
        offspring_info.add_xpath("name", "./td[4]/a")

        offspring_info.add_xpath("breeder", "(.//following-sibling::tr/td/text()[contains(.,'Breeder: ')])[1]")

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(
            item=NZRegistration(), selector=offspring_row
        )

        offspring_registration.add_value("source", "hrnz")

        offspring_registration.add_xpath("name", "./td[4]/a")
        offspring_registration.add_xpath("link", "./td[4]/a/@href")

        offspring.add_value("registrations", offspring_registration.load_item())

        sire = ItemLoader(item=NZHorse())

        sire_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        sire_info.add_value("gender", "horse")

        sire_info.add_xpath("name", "./td[6]/a")

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(item=NZRegistration(), selector=offspring_row)

        sire_registration.add_value("source", "hrnz")

        sire_registration.add_xpath("name", "./td[6]/a")
        sire_registration.add_xpath("link", "./td[6]/a/@href")

        sire.add_value("registrations", sire_registration.load_item())

        offspring.add_value("sire", sire.load_item())

        if offspring_row.xpath('./td[position()=5 and string-length(text())>0]'):
            summary_text = offspring_row.xpath("(.//following-sibling::tr/td/text()[contains(.,'Lt $')])[1]").get()

            if summary_text:
                result_summary = ItemLoader(item=NZResultSummary(), selector=offspring_row)

                result_summary.add_xpath("mark", "./td[5]")

                result_summary.add_value('year', 0)

                summary_text = summary_text[summary_text.find(": ") + 2:]
                summary_splits = summary_text.split(', ')

                result_summary.add_value('starts', summary_splits[0])
                result_summary.add_value('wins', summary_splits[1])
                result_summary.add_value('seconds', summary_splits[2])
                result_summary.add_value('thirds', summary_splits[3])
                result_summary.add_value('earnings', summary_splits[4])

                offspring.add_value('result_summaries', result_summary.load_item())

        horse.add_value("offspring", offspring.load_item())


def parse_dam_sire_offspring(response: Response) -> list[ItemLoader]:
    dams = []
    for offspring_row in response.xpath(
        "//table//tr[td[1]/a[not(text()='Unregistered') and not(text()='Unnamed') and string-length(text())>0]]"
    ):
        dam = ItemLoader(item=NZHorse())

        dam_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        dam_info.add_xpath("name", "./td[6]")

        dam_info.add_value("gender", "mare")

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(item=NZRegistration(), selector=offspring_row)

        dam_registration.add_xpath("name", "./td[6]")
        dam_registration.add_xpath("link", "./td[6]/a/@href")

        dam_registration.add_value("source", "hrnz")

        dam.add_value("registrations", dam_registration.load_item())

        offspring_sire = ItemLoader(item=NZHorse())

        offspring_sire_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        offspring_sire_info.add_xpath("name", "./td[7]")

        offspring_sire_info.add_value("gender", "horse")

        offspring_sire.add_value("horse_info", offspring_sire_info.load_item())

        offspring_sire_registration = ItemLoader(item=NZRegistration(), selector=offspring_row)

        offspring_sire_registration.add_xpath("name", "./td[7]")
        offspring_sire_registration.add_xpath("link", "./td[7]/a/@href")

        offspring_sire_registration.add_value("source", "hrnz")

        offspring_sire.add_value("registrations", offspring_sire_registration.load_item())

        offspring = ItemLoader(item=NZHorse())

        offspring_info = ItemLoader(item=NZHorseInfo(), selector=offspring_row)

        offspring_info.add_xpath("name", "./td[1]")
        offspring_info.add_xpath("gender", "./td[4]")

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=NZRegistration(), selector=offspring_row)

        offspring_registration.add_xpath("name", "./td[1]")
        offspring_registration.add_xpath("link", "./td[1]/a/@href")

        offspring_registration.add_value("source", "hrnz")

        offspring.add_value("registrations", offspring_registration.load_item())

        offspring.add_value("sire", offspring_sire.load_item())

        dam.add_value("offspring", offspring.load_item())

        dams.append(dam)

    return dams