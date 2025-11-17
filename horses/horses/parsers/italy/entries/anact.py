import arrow

from horses.items.italy import (
    ItalianHorseInfo,
    ItalianRaceday,
    ItalianRacedayInfo,
    ItalianRacedayLink,
    ItalianRaceInfo,
    ItalianRaceLink,
    ItalianRaceStarterInfo,
    ItalianRegistration,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response
from parsel import Selector


def parse_anact_calendar(response: Response) -> list[dict]:
    d = []

    for raceday_element in response.xpath("//div[contains(@class,'ippodromo')]"):
        if raceday_element.xpath("./span[contains(text(),'-')]"):
            continue

        raceday = parse_anact_raceday(raceday_element)

        raceday_date = arrow.get(raceday.get_output_value("raceday_info")["date"])

        if raceday_date.date() <= arrow.utcnow().date():
            continue

        races_element = raceday_element.xpath(
            "(.//following-sibling::div[starts-with(@id,'ippodromo-')])[1]")

        races = []

        for race_element in races_element.xpath("./div[contains(@class,'card-header')]"):
            race_info, race_link = parse_anact_race(race_element)

            starters = []

            r = race_element.xpath('(.//following-sibling::div)[1]')

            for row_selector in r.xpath(".//table/tbody/tr"):
                starters.append(parse_anact_starter(row_selector, raceday.get_output_value('raceday_info')['date']))

            races.append(
                {'race_link': race_link, 'race_info': race_info, 'starters': starters})

        raceday_key = (
            f'{raceday.get_output_value("raceday_info")["date"]}_'
            f'{raceday.get_output_value("raceday_info")[
                "racetrack"].replace(" ", "_")}'
        )

        d.append({'raceday': raceday, 'races': races, 'key': raceday_key})

    return d


def parse_anact_raceday(raceday_element: Selector) -> ItemLoader:
    raceday = ItemLoader(item=ItalianRaceday())

    raceday_info = ItemLoader(
        item=ItalianRacedayInfo(), selector=raceday_element)

    raceday_info.add_xpath('racetrack', "./span")
    raceday_info.add_xpath('date', "(.//preceding-sibling::h3)[last()]")

    raceday_info.add_value('country', 'italy')
    raceday_info.add_value('status', 'entries')

    raceday.add_value('raceday_info', raceday_info.load_item())

    raceday_link = ItemLoader(item=ItalianRacedayLink(), selector=raceday_element)

    raceday_link.add_value('source', 'anact')

    raceday_link.add_xpath('link', './@data-target')

    raceday.add_value('links', raceday_link.load_item())

    return raceday


def parse_anact_race(race_element: Selector) -> tuple[ItemLoader, ItemLoader]:
    race_info = ItemLoader(
        item=ItalianRaceInfo(), selector=race_element)

    race_info.add_xpath(
        'racenumber', "substring-before(./span/text(),'-')")
    race_info.add_xpath(
        'racename', "substring-after(./span/text(),'-')")

    race_selector = race_element.xpath(
        "(.//following-sibling::div[starts-with(@id,'corsa-')])[1]")[0]

    race_info.selector = race_selector

    race_info.add_xpath(
        "distance", ".//div[./strong[text()='Distanza:']]/text()")
    race_info.add_xpath(
        "purse", ".//div[./strong[text()='Premio:']]/text()")

    race_link = ItemLoader(item=ItalianRaceLink(), selector=race_element)

    race_link.add_value('source', 'anact')

    race_link.add_xpath('link', "(.//following-sibling::div)[1]/@id")

    return race_info, race_link


def parse_anact_starter(
    row_selector: Selector,
    date: str
) -> dict[str, ItemLoader]:
    starter_info = ItemLoader(
        item=ItalianRaceStarterInfo(), selector=row_selector)

    starter_info.add_xpath("driver", "./td[6]")
    starter_info.add_xpath("distance", "./td[3]")
    starter_info.add_xpath("startnumber", "./td[1]")

    horse_info = ItemLoader(
        item=ItalianHorseInfo(), selector=row_selector)

    horse_info.add_xpath("name", "./td[2]")
    horse_info.add_xpath("gender", "./td[5]")

    if row_selector.xpath('td[position()=4 and string-length(text()) > 0]'):
        age = int(row_selector.xpath("./td[4]/text()").get())

        horse_info.add_value('birthdate', f'{arrow.get(date).year - age}-01-01')

    registration = ItemLoader(
        item=ItalianRegistration(), selector=row_selector)

    registration.add_xpath("name", "./td[2]")
    registration.add_xpath("link", "./td[2]/a/@href")

    registration.add_value("source", "anact")

    return {'starter_info': starter_info, 'horse_info': horse_info, 'registration': registration}
