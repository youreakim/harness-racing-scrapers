from parsel import Selector
import scrapy
from scrapy.http.response import Response
from horses.items.norway import (
    NorwegianHorse,
    NorwegianHorseInfo,
    NorwegianRace,
    NorwegianRaceday,
    NorwegianRacedayInfo,
    NorwegianRaceInfo,
    NorwegianRaceLink,
    NorwegianRaceStarter,
    NorwegianRaceStarterInfo,
    NorwegianRaceStarterOdds,
    NorwegianRaceStarterTime,
    NorwegianRegistration,
    NorwegianResultSummary,
)
from itemloaders import ItemLoader


def handle_ancestor_cell(count: int, cell: Selector) -> ItemLoader | None:
    if not cell.xpath(".//a") or cell.xpath('.//a[contains(text(),"Ukjent ")]'):
        return None

    horse = ItemLoader(item=NorwegianHorse())

    horse_info = ItemLoader(item=NorwegianHorseInfo(), selector=cell)

    horse_info.add_value(
        "gender",
        (
            "horse"
            if count in [0, 1, 2, 3, 6, 9, 10, 13, 16, 17, 18, 21, 24, 25, 28]
            else "mare"
        ),
    )

    horse_info.add_xpath("name", ".//a")
    horse_info.add_xpath("country", ".//a")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=NorwegianRegistration(), selector=cell)

    registration.add_value("source", "DNT")

    registration.add_xpath("name", ".//a")
    registration.add_xpath("link", ".//a/@href")

    horse.add_value("registrations", registration.load_item())

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


def parse_horse(response: Response, horse: ItemLoader) -> None:
    horse_info = ItemLoader(
        item=NorwegianHorseInfo(),
        selector=response.xpath('//div[@class="container"]/div[@class="row"]'),
    )

    horse_info.add_xpath("name", ".//h1")
    horse_info.add_xpath("country", ".//h1")
    horse_info.add_xpath("breed", ".//h1")
    horse_info.add_xpath(
        "birthdate", './/span[contains(text(),"Årgang")]/following-sibling::span'
    )
    horse_info.add_xpath("ueln", './/h3[contains(text(),"578001")]')
    horse_info.add_xpath(
        "gender", './/span[contains(text(),"Kjønn")]/following-sibling::span'
    )
    horse_info.add_xpath(
        "breeder", './/span[contains(text(),"Oppdretter")]/following-sibling::span'
    )

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=NorwegianRegistration(),
        selector=response.xpath('//div[@class="container"]/div[@class="row"]'),
    )

    registration.add_value("link", response.url)
    registration.add_value("source", "DNT")

    registration.add_xpath("name", ".//h1")
    registration.add_xpath("registration", ".//h3")

    horse.add_value("registrations", registration.load_item())

    ancestors = [
        handle_ancestor_cell(count, cell)
        for count, cell in enumerate(
            response.xpath('//div[contains(@class,"pedigree__horse")]')
        )
    ]

    populate_pedigree(horse, ancestors)

    parse_offspring(str(response.body), horse)

    parse_result_summary(str(response.body), horse)

    parse_race_results(str(response.body), horse)


def parse_offspring(page_content: str, horse: ItemLoader) -> None:
    sel = scrapy.Selector(text=page_content)

    for offspring_row in sel.xpath('//section[@id="offspring"]//tbody/tr'):
        offspring = ItemLoader(item=NorwegianHorse())

        offspring_info = ItemLoader(
            item=NorwegianHorseInfo(), selector=offspring_row
        )

        offspring_info.add_xpath("name", "./td[1]")
        offspring_info.add_xpath("birthdate", "./td[2]")
        offspring_info.add_xpath("gender", "./td[4]")

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(
            item=NorwegianRegistration(), selector=offspring_row
        )

        offspring_registration.add_value("source", "DNT")

        offspring_registration.add_xpath("name", "./td[1]")
        offspring_registration.add_xpath("link", "./td[1]/a/@href")

        offspring.add_value("registrations", offspring_registration.load_item())

        if not offspring_row.xpath('./td[position()=6 and text()="0"]'):
            offspring_result_summary = ItemLoader(
                item=NorwegianResultSummary(), selector=offspring_row
            )

            offspring_result_summary.add_value("year", "0")

            offspring_result_summary.add_xpath("starts", "./td[6]")
            offspring_result_summary.add_xpath("wins", "./td[7]")
            offspring_result_summary.add_xpath("seconds", "./td[8]")
            offspring_result_summary.add_xpath("thirds", "./td[9]")
            offspring_result_summary.add_xpath("earnings", "./td[11]")

            offspring.add_value(
                "result_summaries", offspring_result_summary.load_item()
            )

        parent_position = (
            14 if horse.get_output_value("horse_info")["gender"] == "mare" else 15
        )

        if offspring_row.xpath(f"./td[{parent_position}]/a"):
            parent = ItemLoader(item=NorwegianHorse())

            parent_info = ItemLoader(
                item=NorwegianHorseInfo(), selector=offspring_row
            )

            parent_info.add_value(
                "gender", "horse" if parent_position == 14 else "mare"
            )

            parent_info.add_xpath("name", f"./td[{parent_position}]/a")

            parent.add_value("horse_info", parent_info.load_item())

            parent_registration = ItemLoader(
                item=NorwegianRegistration(), selector=offspring_row
            )

            parent_registration.add_value("source", "DNT")

            parent_registration.add_xpath("name", f"./td[{parent_position}]/a")
            parent_registration.add_xpath(
                "link", f"./td[{parent_position}]/a/@href"
            )

            parent.add_value("registrations", parent_registration.load_item())

            offspring.add_value(
                "sire" if parent_position == 14 else "dam", parent.load_item()
            )

        horse.add_value("offspring", offspring.load_item())


def parse_result_summary(page_content: str, horse: ItemLoader) -> None:
    sel = scrapy.Selector(text=page_content)

    for career_row in sel.xpath('//section[@id="career"]//tbody/tr'):
        result_summary = ItemLoader(item=NorwegianResultSummary(), selector=career_row)

        result_summary.add_xpath("year", "./td[1]")
        result_summary.add_xpath("starts", "./td[2]")
        result_summary.add_xpath("wins", "./td[3]")
        result_summary.add_xpath("seconds", "./td[4]")
        result_summary.add_xpath("thirds", "./td[5]")
        result_summary.add_xpath("mark", "./td[7]")
        result_summary.add_xpath("earnings", "./td[8]")

        horse.add_value("result_summaries", result_summary.load_item())


def parse_race_results(page_content: str, horse: ItemLoader) -> None:
    sel = scrapy.Selector(text=page_content)

    for row in sel.xpath("//section[@id='starts']//tbody/tr"):
        raceday = ItemLoader(item=NorwegianRaceday())

        raceday_info = ItemLoader(item=NorwegianRacedayInfo(), selector=row)

        raceday_info.add_xpath("racetrack", "./td[2]")
        raceday_info.add_xpath("date", "./td/time/@datetime")

        raceday.add_value("raceday_info", raceday_info.load_item())

        race = ItemLoader(item=NorwegianRace())

        race_info = ItemLoader(item=NorwegianRaceInfo(), selector=row)

        race_info.add_xpath("racenumber", "./td[4]")

        race.add_value("race_info", race_info.load_item())

        if row.xpath("./td/a[contains(@href,'/results/')]"):
            race_link = ItemLoader(item=NorwegianRaceLink(), selector=row)

            race_link.add_value("source", "DNT")

            race_link.add_xpath("link", "./td/a[contains(@href,'/results/')]/@href")

            race.add_value("links", race_link.load_item())

        starter = ItemLoader(item=NorwegianRaceStarter())

        starter_info = ItemLoader(item=NorwegianRaceStarterInfo(), selector=row)

        starter_info.add_xpath("postposition", "./td[6]")
        starter_info.add_xpath("distance", "./td[5]")
        starter_info.add_xpath("startnumber", "./td[7]")
        starter_info.add_xpath("started", "./td[9]")

        if starter_info.get_output_value("started"):
            starter_info.add_xpath("gallop", "./td[9]")
            starter_info.add_xpath("finished", "./td[9]")
            starter_info.add_xpath("disqualified", "./td[9]")
            starter_info.add_xpath("finish", "./td[10]")
            starter_info.add_xpath("purse", "./td[14]")

            if row.xpath("./td[position()=9 and contains(text(),',')]"):
                starter_time = ItemLoader(item=NorwegianRaceStarterTime(), selector=row)

                starter_time.add_xpath("time", "./td[9]")

                starter_time.add_value("from_distance", 0)
                starter_time.add_value("to_distance", starter_info.get_output_value("distance"))
                starter_time.add_value("time_format", "kilometer")

                starter.add_value("times", starter_time.load_item())

            if row.xpath("./td[position()=13 and number(text())]"):
                odds = ItemLoader(item=NorwegianRaceStarterOdds(), selector=row)

                odds.add_xpath("odds", "./td[13]")

                odds.add_value("odds_type", "win")

                starter.add_value("odds", odds.load_item())

        starter.add_value("starter_info", starter_info.load_item())

        race.add_value("race_starters", starter.load_item())

        raceday.add_value("races", race.load_item())

        horse.add_value("starts", raceday.load_item())
