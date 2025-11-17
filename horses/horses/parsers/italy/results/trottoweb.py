import arrow
from horses.items.italy import (
    ItalianHorseInfo,
    ItalianRacedayInfo,
    ItalianRacedayLink,
    ItalianRaceInfo,
    ItalianRaceStarter,
    ItalianRaceStarterInfo,
    ItalianRaceStarterTime,
    ItalianRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_trottoweb_calendar(
    response: Response,
    start_date: arrow.arrow.Arrow,
    end_date: arrow.arrow.Arrow
) -> list[dict]:
    racedays = []
    
    for raceday_row in response.xpath("//tr[.//a[text()='RISULTATI']]"):
        result_link = raceday_row.xpath(
            ".//a[text()='RISULTATI']/@href").get()

        raceday_date = arrow.get(
            result_link[
                result_link.find("&data") + 6: result_link.find("&ippodromo")
            ]
        )

        if start_date.date() <= raceday_date.date() <= end_date.date():
            raceday_info, raceday_link = parse_trottoweb_raceday(
                raceday_row, raceday_date, result_link
            )

            key = f'{raceday_date.date().isoformat()}_{
                raceday_info.get_output_value("racetrack")}'

            racedays.append({'raceday_info': raceday_info, 'key': key, 'raceday_link': raceday_link, 'url': f'https://www.trottoweb.it/TrottoWeb/php/{result_link}'})

    return racedays


def parse_trottoweb_raceday(
    selector: Selector,
    raceday_date: arrow.arrow.Arrow,
    result_link: str
) -> tuple[ItemLoader, ItemLoader]:
    raceday_info = ItemLoader(item=ItalianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "result")
    raceday_info.add_value("date", raceday_date.date().isoformat())

    raceday_info.add_xpath("racetrack", ".//span[@class='nome_ippo']")

    raceday_link = ItemLoader(item=ItalianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "trottoweb")
    raceday_link.add_value("link", result_link)

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

    for order, starter_element in enumerate(selector.xpath(".//tr"), 1):
        starters.append(parse_trottoweb_starter(starter_element, order))

    return {
        "race_info": race_info,
        "race_link": None,
        "starters": starters,
    }


def parse_trottoweb_starter(selector: Selector, order: int) -> dict[str, ItemLoader | list]:
    starter = ItemLoader(item=ItalianRaceStarter())

    starter_info = ItemLoader(item=ItalianRaceStarterInfo(), selector=selector)

    starter_info.add_xpath('finish', './td[@class="piaz_u"]')
    starter_info.add_xpath('startnumber', './td[contains(@class,"num_part")]')
    starter_info.add_xpath('distance', './td[@class="dist_cav_u"]')
    starter_info.add_xpath('driver', './td[@class="driver_u"]')

    times = []

    if selector.xpath('./td[@class="tempo_u" and number(text())]'):
        starter_time = ItemLoader(item=ItalianRaceStarterTime(), selector=selector)

        starter_time.add_xpath('time', './td[@class="tempo_u"]')

        starter_time.add_value('time_format', 'kilometer')
        starter_time.add_value('from_distance', 0)
        starter_time.add_value('to_distance', starter_info.get_output_value('distance'))

        times.append(starter_time)

    if selector.xpath('./td[@class="premio_u"]/span'):
        starter_info.add_xpath('purse', './td[@class="premio_u"]/span')

    starter_info.add_value('started', False if selector.xpath("./td[@class='nome_cav_rit_u']") else True)
    starter_info.add_value('disqualified', True if selector.xpath("./td[@class='tempo_u' and ./span[text()='r.p.']]") else False)
    starter_info.add_value('finished', False if selector.xpath("./td[@class='tempo_u' and ./span[text()='rit.']]") else True)

    starter_info.add_value('order', order)

    starter.add_value("starter_info", starter_info.load_item())

    horse_info = ItemLoader(item=ItalianHorseInfo(), selector=selector)

    horse_info.add_xpath('name', './td[contains(@class,"nome_cav")]/a')

    registration = ItemLoader(item=ItalianRegistration(), selector=selector)

    registration.add_xpath('name', './td[contains(@class,"nome_cav")]/a')
    registration.add_xpath('link', './td[contains(@class,"nome_cav")]/a/@href')

    registration.add_value('source', 'trottoweb')

    return {'starter_info': starter_info, 'horse_info': horse_info, 'registration': registration, 'times': times}
