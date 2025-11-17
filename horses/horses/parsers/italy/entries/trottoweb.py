from horses.items.italy import (
    ItalianHorseInfo,
    ItalianRacedayInfo,
    ItalianRacedayLink,
    ItalianRaceInfo,
    ItalianRaceStarterInfo,
    ItalianRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_trottoweb_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_row in response.xpath(
        "//tr[td[@class='dati_ippo'] and .//a[text()='PARTENTI']]"
    ):
        raceday_info, raceday_link = parse_trottoweb_raceday(raceday_row)

        link = (
            f"https://www.trottoweb.it/TrottoWeb/php/hPart.php?"
            f"{raceday_link.get_output_value('link')}"
        )

        raceday_key = (
            f'{raceday_info.get_output_value("date")}_'
            f'{raceday_info.get_output_value("racetrack").replace(" ", "_")}'
        )

        racedays.append({"raceday_info": raceday_info, "key": raceday_key, 'raceday_link': raceday_link, 'url': link})

    return racedays


def parse_trottoweb_raceday(selector: Selector) -> tuple[ItemLoader, ItemLoader]:
    raceday_info = ItemLoader(item=ItalianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "entries")
    raceday_info.add_xpath(
        "date", ".//a[text()='PARTENTI']/@href[contains(.,'hPart.php?')]"
    )

    raceday_info.add_xpath("racetrack", ".//span[@class='nome_ippo']")

    raceday_link = ItemLoader(item=ItalianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "trottoweb")

    raceday_link.add_xpath(
        "link", ".//a[text()='PARTENTI']/@href[contains(.,'hPart.php')]"
    )

    return raceday_info, raceday_link


def parse_trottoweb_races(response: Response) -> list[dict]:
    return [parse_trottoweb_race(race_selector) for race_selector in response.xpath("//div[contains(@id,'corsa_') and @class]")]


def parse_trottoweb_race(selector: Selector) -> dict:
    race_info = ItemLoader(item=ItalianRaceInfo(), selector=selector)

    race_info.add_xpath("racenumber", ".//div[@class='numero_corsa']")
    race_info.add_xpath("racename", ".//div[@class='nome_corsa']/text()")
    race_info.add_xpath("purse", ".//div[@class='montepremi']/text()")
    race_info.add_xpath("conditions", ".//div[@class='prop_corsa']")
    race_info.add_xpath("distance", ".//span[@class='dist_corsa']")

    starters = []

    postposition = 1

    for starter_element in selector.xpath(".//tr"):
        if starter_element.xpath('./td[@colspan]'):
            postposition = 1
            continue

        starters.append(parse_trottoweb_starter(starter_element, postposition))

        postposition += 1

    return {
        "race_info": race_info,
        "race_link": None,
        "starters": starters,
    }


def parse_trottoweb_starter(selector: Selector, postposition) -> dict[str, ItemLoader]:
    starter_info = ItemLoader(item=ItalianRaceStarterInfo(), selector=selector)

    starter_info.add_xpath('startnumber', './td[contains(@class,"num_part")]')
    starter_info.add_xpath('distance', './td[@class="dist_cav"]')
    starter_info.add_xpath('driver', './td[@class="driver"]')

    starter_info.add_value('postposition', postposition)

    horse_info = ItemLoader(item=ItalianHorseInfo(), selector=selector)

    horse_info.add_xpath('name', './td[contains(@class,"nome_cav")]/a')

    registration = ItemLoader(item=ItalianRegistration(), selector=selector)

    registration.add_xpath('name', './td[contains(@class,"nome_cav")]/a')
    registration.add_xpath('link', './td[contains(@class,"nome_cav")]/a/@href')

    registration.add_value('source', 'trottoweb')

    return {'starter_info': starter_info, 'horse_info': horse_info, 'registration': registration}
