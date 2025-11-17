from parsel import Selector
from scrapy.http.response import Response
from horses.items.italy import (
    ItalianHorseInfo,
    ItalianRacedayInfo,
    ItalianRacedayLink,
    ItalianRaceInfo,
    ItalianRaceLink,
    ItalianRaceStarterInfo,
    ItalianRaceStarterOdds,
    ItalianRaceStarterTime,
    ItalianRegistration,
)
from itemloaders import ItemLoader


def parse_snai_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_section in response.xpath(
        '//div[contains(@class,"list-group-item") and .//a[contains(@href,"risultati/T/IT")]]'
    ):
        raceday_info, raceday_link = parse_snai_raceday(raceday_section, response)

        race_links = raceday_section.xpath(
            './/a[contains(@class,"button") and contains(@title," corsa ")]/@href'
        ).getall()

        key = f'{raceday_info.get_output_value("date")}_{
            raceday_info.get_output_value("racetrack")}'

        racedays.append({'raceday_info': raceday_info, 'key': key, 'raceday_link': raceday_link, 'race_links': race_links})
    
    return racedays


def parse_snai_raceday(selector: Selector, response: Response) -> tuple[ItemLoader, ItemLoader]:
    raceday_info = ItemLoader(item=ItalianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "result")
    raceday_info.add_value("date", response.url.split("/")[-1])
    raceday_info.add_value("country", "italy")

    raceday_info.add_xpath(
        "racetrack",
        './/a[contains(@class,"is-snai-2")]/span[not(@class="icon")]',
    )

    raceday_link = ItemLoader(item=ItalianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "snai")

    raceday_link.add_value("link", response.url)

    return raceday_info, raceday_link


def parse_snai_race(response: Response) -> dict[str, ItemLoader]:
    race_info = ItemLoader(
        item=ItalianRaceInfo(),
        selector=response.xpath('//div[contains(@class,"message ")]'),
    )

    race_info.add_value("status", "result")

    race_info.add_xpath("racenumber", './div[@class="message-header"]')
    race_info.add_xpath("racename", './/h4[contains(@class,"is-5")]/text()')
    race_info.add_xpath(
        "distance",
        'substring-after(.//h4[contains(@class,"is-5")]/small/text(),"Metri")',
    )
    race_info.add_xpath(
        "purse",
        'substring-before(substring-after(.//h4[contains(@class,"is-5")]/small/text()[1],"Euro")," - ")',
    )
    race_info.add_xpath("conditions", ".//p[em]")

    race_link = ItemLoader(item=ItalianRaceLink())

    race_link.add_value("source", "snai")
    race_link.add_value("link", response.url)

    return {
        "race_info": race_info,
        "race_link": race_link,
    }


def parse_snai_starter(selector: Selector, order: int, year: int, odds: dict) -> dict:
    starter_info = ItemLoader(item=ItalianRaceStarterInfo(), selector=selector)

    starter_info.add_xpath('finish', './/h4/text()')
    starter_info.add_xpath('startnumber', './/h4/small')
    starter_info.add_xpath('distance', './/span[@title="distanza"]')
    starter_info.add_xpath('driver', './/a[contains(@href,"/driver/")]/span')
    starter_info.add_xpath('trainer', './/a[contains(@href,"/allenatore/")]/span[not(@class)]')
    starter_info.add_xpath('started', './/h4/text()')
    starter_info.add_xpath('disqualified', './/h4/text()')
    starter_info.add_xpath('finished', './/h4/text()')

    starter_info.add_value('order', order)
    
    times = []

    if selector.xpath('.//span[@title="tempo"]'):
        starter_time = ItemLoader(item=ItalianRaceStarterTime(), selector=selector)

        starter_time.add_xpath('time', './/span[@title="tempo"]')

        starter_time.add_value('from_distance', 0)
        starter_time.add_value('to_distance', starter_info.get_output_value('distance'))
        starter_time.add_value('time_format', 'kilometer')

        times.append(starter_time)

    o = []

    if selector.xpath('.//span[contains(@title,"totalizzatore")]'):
        starter_odds = ItemLoader(item=ItalianRaceStarterOdds(), selector=selector)

        starter_odds.add_xpath('odds', './/span[contains(@title,"totalizzatore")]')

        starter_odds.add_value('odds_type', 'win')

        o.append(starter_odds.load_item())

    if starter_info.get_output_value('startnumber') in odds:
        o.extend(odds[starter_info.get_output_value('startnumber')])

    horse_info = ItemLoader(item=ItalianHorseInfo(), selector=selector)

    horse_info.add_xpath('name', './/a[contains(@title," cavallo ")]/span[1]')
    horse_info.add_xpath('gender', 'substring(.//span[contains(@class,"tag-info-cavallo")]/text(),1,1)')
    
    age_string = selector.xpath('.//span[contains(@class,"tag-info-cavallo")]/text()').get()

    if age_string:
        age = ''.join(x for x in age_string if x.isnumeric())

        if age != '':
            horse_info.add_value('birthdate', f'{year - int(age)}-01-01')

    registration = ItemLoader(item=ItalianRegistration(), selector=selector)

    registration.add_xpath('name', './/a[contains(@title," cavallo ")]/span[1]')
    registration.add_xpath('link', './/a[contains(@title," cavallo ")]/@href')

    registration.add_value('source', 'snai')
    
    return {'starter_info': starter_info, 'horse_info': horse_info, 'registration': registration, 'times': times, 'odds': o}
