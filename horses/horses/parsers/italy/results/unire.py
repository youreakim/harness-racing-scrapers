import arrow
from parsel import Selector
from scrapy.http.response import Response
from horses.items.italy import (
    ItalianHorseInfo,
    ItalianRacedayInfo,
    ItalianRacedayLink,
    ItalianRaceInfo,
    ItalianRaceLink,
    ItalianRaceStarterInfo,
    ItalianRaceStarterTime,
    ItalianRegistration,
)
from itemloaders import ItemLoader


def parse_unire_calendar(
    response: Response,
    start_date: arrow.arrow.Arrow,
    end_date: arrow.arrow.Arrow
) -> list[dict]:
    racedays = []

    for raceday_row in response.xpath(
        '//table[@class="tableholder"]//tr[./td[(position()=4 and text()="T")] and .//a[contains(text(),",")]]'
    ):
        raceday_info, raceday_link = parse_unire_raceday(raceday_row)

        raceday_date = arrow.get(raceday_info.get_output_value('date'))

        if start_date.date() <= raceday_date.date() <= end_date.date():
            key = f'{raceday_info.get_output_value("date")}_{
                raceday_info.get_output_value("racetrack")}'

            racedays.append({'raceday_info': raceday_info, 'key': key, 'raceday_link': raceday_link})

    return racedays

def parse_unire_raceday(selector: Selector) -> tuple[ItemLoader, ItemLoader]:
    raceday_info = ItemLoader(item=ItalianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "result")
    raceday_info.add_value("country", "italy")

    raceday_info.add_xpath("racetrack", 'substring-before(.//a/text(),",")')
    raceday_info.add_xpath("date", "./td[1]")

    raceday_link = ItemLoader(item=ItalianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "unire")

    raceday_link.add_xpath("link", ".//a/@href")

    return raceday_info, raceday_link


def parse_unire_race(response: Response) -> dict[str, ItemLoader | list]:
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


def parse_unire_starter(selector: Selector) -> dict[str, ItemLoader | list]:
    starter_info = ItemLoader(item=ItalianRaceStarterInfo(), selector=selector)

    if selector.xpath('./td[position()=1 and string-length(text())>0]'):
        starter_info.add_xpath('finish', './td[1]')

        starter_info.add_value('started', True)
    else:
        starter_info.add_value('started', False)

    starter_info.add_xpath('startnumber', './td[2]')
    starter_info.add_xpath('driver', './td[4]')
    starter_info.add_xpath('distance', './td[5]')

    times = []

    if selector.xpath('./td[position()=6 and number(text())]'):
        starter_time = ItemLoader(item=ItalianRaceStarterTime(), selector=selector)

        starter_time.add_xpath('time', './td[6]')

        starter_time.add_value('from_distance', 0)
        starter_time.add_value('to_distance', starter_info.get_output_value('distance'))
        starter_time.add_value('time_format', 'kilometer')

        times.append(starter_time)

    horse_info = ItemLoader(item=ItalianHorseInfo(), selector=selector)

    horse_info.add_xpath('name', './td[3]')

    registration = ItemLoader(item=ItalianRegistration(), selector=selector)

    if selector.xpath('.//a'):
        registration.add_xpath('name', './/a')
        registration.add_xpath('link', './/a/@href')

        registration.add_value('source', 'unire')

    return {'starter_info': starter_info, 'horse_info': horse_info, 'registration': registration, 'times': times}
