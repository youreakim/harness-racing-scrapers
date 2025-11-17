from horses.items.italy import (
    ItalianHorseInfo,
    ItalianRace,
    ItalianRacedayInfo,
    ItalianRacedayLink,
    ItalianRaceInfo,
    ItalianRaceLink,
    ItalianRaceStarterInfo,
    ItalianRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response



def parse_unire_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_row in response.xpath(
        '//table[@class="tableholder"]//tr[td[text()="T"] and td/a[contains(text(),",")]]'
    ):
        raceday_info, raceday_link = parse_unire_raceday(raceday_row)

        raceday_key = (
            f'{raceday_info.get_output_value("date")}_'
            f'{raceday_info.get_output_value("racetrack").replace(" ", "_")}'
        )

        racedays.append({"raceday_info": raceday_info, "raceday_link": raceday_link, "key": raceday_key})

    return racedays


def parse_unire_race_links(response: Response) -> list[str]:
    return response.xpath("//table//a/@href").getall()


def parse_unire_raceday(selector: Selector) -> tuple[ItemLoader, ItemLoader]:
    raceday_info = ItemLoader(item=ItalianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "entries")

    raceday_info.add_xpath("racetrack", 'substring-before(.//a/text(),",")')
    raceday_info.add_xpath("date", "./td[1]")

    raceday_link = ItemLoader(item=ItalianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "unire")

    raceday_link.add_xpath("link", ".//a/@href")

    return raceday_info, raceday_link


def parse_unire_race(response: Response) -> dict:
    url_splits = response.url.split("/")

    racenumber = int(url_splits[url_splits.index("n_corsa") + 1])

    race_info = ItemLoader(item=ItalianRaceInfo())

    race_info.add_value("racenumber", racenumber)

    race_link = ItemLoader(item=ItalianRaceLink())

    race_link.add_value("link", response.url)
    race_link.add_value("source", "unire")

    starters = []

    for starter_row in response.xpath('//table[@class="tableholder"]//tr[not(@class)]'):
        starters.append(parse_unire_starter(starter_row))

    return {
        "race_info": race_info,
        "race_link": race_link,
        "starters": starters,
    }


def parse_unire_race_info(
    response: Response,
) -> tuple[ItemLoader, ItemLoader, ItemLoader]:
    race = ItemLoader(item=ItalianRace())

    race_info = ItemLoader(
        item=ItalianRaceInfo(),
        selector=response.xpath(
            '//table//td[@colspan="9" and contains(b/text()," E.")]'
        ),
    )

    race_info.add_value("racenumber", response.url)

    race_info.add_xpath("racename", 'substring-before(.//text()," E.")')
    race_info.add_xpath(
        "purse", 'substring-after(substring-before(.//text()," M.")," E.")'
    )
    race_info.add_xpath(
        "distance", 'substring-before(substring-after(.//text()," M."),"-")'
    )

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(
        item=ItalianRaceLink(),
        selector=response.xpath(
            '//table//td[@colspan="9" and contains(b/text()," E.")]'
        ),
    )

    race_link.add_value("source", "unire")
    race_link.add_value("link", response.url)

    return race, race_info, race_link


def parse_unire_starter(
    selector: Selector,
) -> dict[str, ItemLoader | None]:
    starter_info = ItemLoader(item=ItalianRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("startnumber", "./td[2]")
    starter_info.add_xpath("driver", "./td[4]")
    starter_info.add_xpath("distance", "./td[5]")

    horse_info = ItemLoader(item=ItalianHorseInfo(), selector=selector)

    horse_info.add_xpath("name", "./td[3]")

    registration = None

    if selector.xpath(".//a"):
        registration = ItemLoader(item=ItalianRegistration(), selector=selector)

        registration.add_value("source", "unire")

        registration.add_xpath("name", ".//a")
        registration.add_xpath("link", ".//a/@href")

    return {'starter_info': starter_info, 'horse_info': horse_info, 'registration': registration}
