from horses.items.holland import (
    DutchHorse,
    DutchHorseInfo,
    DutchRace,
    DutchRaceday,
    DutchRacedayInfo,
    DutchRacedayLink,
    DutchRaceInfo,
    DutchRaceLink,
    DutchRaceStarter,
    DutchRaceStarterInfo,
    DutchRaceStarterOdds,
    DutchRaceStarterTime,
    DutchRegistration,
    DutchResultSummary,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def handle_cell(cell: Selector) -> ItemLoader | None:
    if cell.xpath('./strong[text()="N.V.T."]'):
        return None

    horse = ItemLoader(item=DutchHorse())

    horse_info = ItemLoader(item=DutchHorseInfo(), selector=cell)

    horse_info.add_xpath("name", "./strong")
    horse_info.add_xpath("gender", "./text()[1]")
    horse_info.add_xpath("birthdate", './text()[contains(.,"-")]')

    horse.add_value("horse_info", horse_info.load_item())

    return horse


def add_parents(
    horse: ItemLoader | None, sire: ItemLoader | None, dam: ItemLoader | None
) -> None:
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


def parse_search_result(response: Response, search: str) -> list[str]:
    ids = []

    for row in response.xpath("//div[@id='ndr-search-results']//li"):
        name = row.xpath(".//div[@class='ndr-result-naam']/text()").get()

        if name and name.strip().lower().startswith(search.lower()):
            ids.append(row.xpath(".//div[@class='ndr-result-id']/text()").get())

    return ids


def parse_horse(response: Response, link: str, horse: ItemLoader) -> ItemLoader:
    horse_info = ItemLoader(
        item=DutchHorseInfo(), selector=response.xpath('//div[@id="ndr-tab-algemeen"]')
    )

    horse_info.add_value("breed", "standardbred")

    horse_info.add_xpath("name", './/label[text()="Naam"]/following-sibling::span[1]')
    horse_info.add_xpath(
        "gender", './/label[text()="Geslacht"]/following-sibling::span[1]'
    )
    horse_info.add_xpath(
        "birthdate", './/label[text()="Geboortedatum"]/following-sibling::span[1]'
    )
    horse_info.add_xpath(
        "breeder", './/label[text()="Fokker"]/following-sibling::span[1]'
    )

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=DutchRegistration(),
        selector=response.xpath('//div[@id="ndr-tab-algemeen"]'),
    )

    registration.add_value("source", "ndr")
    registration.add_value("link", link)

    registration.add_xpath(
        "registration", './/label[text()="Stamboeknummer"]/following-sibling::span[1]'
    )
    registration.add_xpath("name", './/label[text()="Naam"]/following-sibling::span[1]')

    horse.add_value("registrations", registration.load_item())

    ancestors = [
        handle_cell(x)
        for x in response.xpath('//div[@id="ndr-tab-stamboom"]//td[@rowspan!="16"]')
    ]

    populate_pedigree(horse, ancestors)

    result_summary = ItemLoader(
        item=DutchResultSummary(),
        selector=response.xpath('//div[@id="ndr-tab-record"]'),
    )

    result_summary.add_xpath(
        "starts", './/label[text()="Aantal gestart"]/following-sibling::text()[1]'
    )
    result_summary.add_xpath(
        "wins", './/label[text()="Overwinningen totaal"]/following-sibling::text()[1]'
    )
    result_summary.add_xpath(
        "earnings",
        './/label[text()="Werkelijke winsom totaal"]/following-sibling::text()[1]',
    )
    result_summary.add_xpath(
        "mark", './/label[text()="Recordtijd"]/following-sibling::text()[1]'
    )

    horse.add_value("result_summaries", result_summary.load_item())

    for start_row in response.xpath(
        '//div[@id="ndr-tab-verrichtingen"]//tr[@data-koersdag]'
    ):
        horse.add_value("starts", parse_start(start_row))

    parse_offspring(response, horse)

    return horse


def parse_start(selector: Selector) -> dict:
    raceday = ItemLoader(item=DutchRaceday())

    raceday_info = ItemLoader(item=DutchRacedayInfo(), selector=selector)

    raceday_info.add_xpath("date", './td[@class="ndr-verrichting-datum"]')
    raceday_info.add_xpath("racetrack", './td[@class="ndr-verrichting-baan"]')

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=DutchRacedayLink(), selector=selector)

    raceday_link.add_value("source", "ndr")

    raceday_link.add_xpath("link", "./@data-koersdag")

    raceday.add_value("links", raceday_link.load_item())

    race = ItemLoader(item=DutchRace())

    race_info = ItemLoader(item=DutchRaceInfo(), selector=selector)

    race_info.add_xpath("distance", './td[@class="ndr-verrichting-afstand"]')
    race_info.add_xpath("startmethod", './td[@class="ndr-verrichting-start"]')
    race_info.add_xpath("racenumber", './td[@class="ndr-verrichting-koersnr"]')

    race.add_value("race_info", race_info.load_item())

    race_starter = ItemLoader(item=DutchRaceStarter())

    starter_info = ItemLoader(item=DutchRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("finish", './td[@class="ndr-verrichting-plaats"]')
    starter_info.add_xpath("driver", './td[@class="ndr-verrichting-rijder"]')
    starter_info.add_xpath("purse", './td[@class="ndr-verrichting-prijs"]')

    race_starter.add_value("starter_info", starter_info.load_item())

    starter_odds = ItemLoader(item=DutchRaceStarterOdds(), selector=selector)

    starter_odds.add_value("odds_type", "win")

    starter_odds.add_xpath("odds", './td[@class="ndr-verrichting-cote"]')

    race_starter.add_value("odds", starter_odds.load_item())

    starter_time = ItemLoader(item=DutchRaceStarterTime(), selector=selector)

    starter_time.add_value("from_distance", 0)
    starter_time.add_value("to_distance", starter_info.get_output_value("distance"))
    starter_time.add_value("time_format", "km")

    starter_time.add_xpath("time", './td[@class="ndr-verrichting-tijd"]')

    race_starter.add_value("times", starter_time.load_item())

    race.add_value("race_starters", race_starter.load_item())

    raceday.add_value("races", race.load_item())

    return raceday.load_item()


def parse_offspring(response: Response, horse: ItemLoader) -> None:
    for row in response.xpath("//div[@id='ndr-tab-afstammelingen']//tbody/tr"):
        offspring = ItemLoader(item=DutchHorse())

        offspring_info = ItemLoader(item=DutchHorseInfo(), selector=row)

        offspring_info.add_xpath("birthdate", "./td[1]")
        offspring_info.add_xpath("name", "./td[2]")
        offspring_info.add_xpath("gender", "./td[3]")

        offspring.add_value("horse_info", offspring_info.load_item())

        horse.add_value("offspring", offspring.load_item())
