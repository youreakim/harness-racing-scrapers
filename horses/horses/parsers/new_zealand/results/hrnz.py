import arrow
from parsel import Selector
import scrapy
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
    NZRaceStarterTime,
    NZRegistration,
)
from itemloaders import ItemLoader
from scrapy_playwright.page import PageMethod

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "//table//tr//a")],
}


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_row in response.xpath("//tr[td/a]"):
        raceday = ItemLoader(item=NZRaceday())

        raceday_info = ItemLoader(item=NZRacedayInfo(), selector=raceday_row)

        raceday_info.add_xpath("racetrack", "./td[1]")
        raceday_info.add_xpath("date", "./td[3]/text()")

        raceday.add_value("raceday_info", raceday_info.load_item())

        raceday_link = ItemLoader(item=NZRacedayLink(), selector=raceday_row)

        raceday_link.add_value("source", "hrnz")

        raceday_link.add_xpath("link", "./td[1]/a/@href")

        raceday.add_value("links", raceday_link.load_item())

        raceday_date = arrow.get(
            raceday_info.get_output_value("date"), "YYYY-MM-DD"
        ).date()

        requests = [
            (
                scrapy.Request,
                {
                    "url": f'https://harness.hrnz.co.nz{raceday_row.xpath("./td[1]/a/@href").get()}',
                    "meta": META_RACEDAY,
                },
            )
        ]
        racedays.append({"raceday": raceday, 'raceday_date': raceday_date, "requests": requests})

    return racedays


def parse_race(response: Response) -> ItemLoader:
    race = ItemLoader(item=NZRace())

    race_info = ItemLoader(
        item=NZRaceInfo(),
        selector=response.xpath('//div[contains(@class,"hrnz-datalist--inline")]'),
    )

    race_info.add_value("status", "result")
    race_info.add_value("racetype", "race")

    race_info.add_xpath(
        "racenumber", 'substring-after(substring-before(./h5/text()," - "),"Race ")'
    )
    race_info.add_xpath(
        "racename", 'substring-before(substring-after(./h5/text()," - "),", $")'
    )
    race_info.add_xpath(
        "purse", 'substring-before(substring-after(./h5/text(),", $"),", ")'
    )
    race_info.add_xpath(
        "distance", "substring(./h5/text(),string-length(./h5/text())-5)"
    )
    race_info.add_xpath("gait", "./h5")
    race_info.add_xpath("startmethod", "./h5")

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=NZRaceLink())

    race_link.add_value("source", "hrnz")
    race_link.add_value("link", response.url)

    race.add_value("links", race_link.load_item())

    order = 0

    for order, starter_row in enumerate(
        response.xpath("//tbody/tr[not(@class) and .//a]"), 1
    ):
        starter = parse_starter(starter_row, order, race_info)

        race.add_value('race_starters', starter.load_item())

    for order, scratch_row in enumerate(response.xpath("//tr[td[@data-label='Placing' and text()='SCR']]"), order + 1):
        starter = parse_scratched(scratch_row, order)

        race.add_value('race_starters', starter.load_item())

    return race


def parse_scratched(selector: Selector, order: int) -> ItemLoader:
    starter = ItemLoader(item=NZRaceStarter())

    starter_info = ItemLoader(item=NZRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("startnumber", './td[@data-label="Book"]')

    starter_info.add_value('order', order)

    starter_info.add_value("started", False)

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=NZHorse())

    horse_info = ItemLoader(item=NZHorseInfo(), selector=selector)

    horse_info.add_xpath("name", "./td[@data-label='Horse']/span")

    horse.add_value("horse_info", horse_info.load_item())

    starter.add_value("horse", horse.load_item())

    return starter

def parse_starter(selector: Selector, order: int, race_info: ItemLoader) -> ItemLoader:
    race_starter = ItemLoader(item=NZRaceStarter())

    starter_info = ItemLoader(item=NZRaceStarterInfo(), selector=selector)

    starter_info.add_value("order", order)

    starter_info.add_xpath("finish", './td[@data-label="Placing"]')
    starter_info.add_xpath("startnumber", './td[@data-label="Book"]')
    starter_info.add_xpath("purse", './td[@data-label="Stakes"]')
    starter_info.add_xpath("driver", './td[@data-label="Driver"]')
    starter_info.add_xpath("trainer", './td[@data-label="Trainer"]')
    starter_info.add_value("distance", race_info.get_output_value("distance"))

    if selector.xpath("./td[@data-label='HCP' and contains(text(),'m')]"):
        starter_info.add_xpath("distance", "./td[@data-label='HCP']")

    race_starter.add_value("starter_info", starter_info.load_item())

    starter_time = ItemLoader(item=NZRaceStarterTime(), selector=selector)

    starter_time.add_value("from_distance", 0)
    starter_time.add_value(
        "to_distance", starter_info.get_output_value("distance")
    )
    starter_time.add_value("time_format", "total")

    starter_time.add_xpath("time", './td[@data-label="Time"]')

    race_starter.add_value("times", starter_time.load_item())

    horse = ItemLoader(item=NZHorse())

    horse_info = ItemLoader(item=NZHorseInfo(), selector=selector)

    horse_info.add_xpath("name", './td[@data-label="Horse"]')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=NZRegistration(), selector=selector)

    registration.add_value("source", "hrnz")

    registration.add_xpath("name", './td[@data-label="Horse"]')
    registration.add_xpath("link", './td[@data-label="Horse"]/a/@href')

    horse.add_value("registrations", registration.load_item())

    if starter_info.get_output_value("finish") < 4:
        pedigree_selector = selector.xpath(
            f"(.//ancestor::div[@class='hrnz-race-video__wrapper']"
            f"//div[@class='hrnz-placed-horses__wrapper' and "
            f".//a[contains(@href,'{registration.get_output_value('link')}')]])[last()]"
        )

        sire = ItemLoader(item=NZHorse())

        sire_info = ItemLoader(item=NZHorseInfo(), selector=pedigree_selector)

        sire_info.add_value("gender", "horse")

        sire_info.add_xpath("name", './/div[@data-label="Pedigree"]/a[1]')

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(item=NZRegistration(), selector=pedigree_selector)

        sire_registration.add_value("source", "hrnz")

        sire_registration.add_xpath(
            "name", './/div[@data-label="Pedigree"]/a[1]'
        )
        sire_registration.add_xpath(
            "link", './/div[@data-label="Pedigree"]/a[1]/@href'
        )

        sire.add_value("registrations", sire_registration.load_item())

        horse.add_value("sire", sire.load_item())

        dam = ItemLoader(item=NZHorse())

        dam_info = ItemLoader(item=NZHorseInfo(), selector=pedigree_selector)

        dam_info.add_value("gender", "mare")

        dam_info.add_xpath("name", './/div[@data-label="Pedigree"]/a[2]')

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(item=NZRegistration(), selector=pedigree_selector)

        dam_registration.add_value("source", "hrnz")

        dam_registration.add_xpath(
            "name", './/div[@data-label="Pedigree"]/a[2]'
        )
        dam_registration.add_xpath(
            "link", './/div[@data-label="Pedigree"]/a[2]/@href'
        )

        dam.add_value("registrations", dam_registration.load_item())

        horse.add_value("dam", dam.load_item())

    race_starter.add_value("horse", horse.load_item())

    return race_starter
