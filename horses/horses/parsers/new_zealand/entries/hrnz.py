from parsel import Selector
from horses.items.new_zealand import (
    NZHorse,
    NZHorseInfo,
    NZRace,
    NZRaceday,
    NZRacedayInfo,
    NZRacedayLink,
    NZRaceInfo,
    NZRaceStarter,
    NZRaceStarterInfo,
    NZRegistration,
)
from itemloaders import ItemLoader


def parse_raceday(selector: Selector) -> ItemLoader:
    raceday = ItemLoader(item=NZRaceday())

    raceday_info = ItemLoader(item=NZRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "entries")

    raceday_info.add_xpath("racetrack", './td[@data-label="Name"]')
    raceday_info.add_xpath("date", './td[@data-label="Date"]')

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=NZRacedayLink(), selector=selector)

    raceday_link.add_value("source", "hrnz")

    raceday_link.add_xpath("link", './td[@data-label="Name"]/a/@href')

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(selector: Selector) -> ItemLoader:
    race = ItemLoader(item=NZRace())

    race_info = ItemLoader(item=NZRaceInfo(), selector=selector)

    race_info.add_xpath(
        "racenumber",
        'substring-after(.//dd[contains(text(),"Race ")]/text()," ")',
    )
    race_info.add_xpath("racename", './/div[@class="hrnz-race__name"]/h3')
    race_info.add_xpath("startmethod", './/div[@class="hrnz-race__name"]/h3')
    race_info.add_xpath("gait", './/div[@class="hrnz-race__name"]/h3')
    race_info.add_xpath(
        "purse", 'substring-before(.//div[@class="hrnz-race__name"]/h4,", ")'
    )
    race_info.add_xpath(
        "conditions",
        ".//div[@class='hrnz-race__conditions']/p"
    )
    race_info.add_xpath(
        "distance",
        'substring(.//div[@class="hrnz-race__name"]/h4/text(),string-length(.//div[@class="hrnz-race__name"]/h4/text())-5)',
    )

    race_info.add_value("status", "entries")
    race_info.add_value("racetype", "race")

    race.add_value("race_info", race_info.load_item())

    for starter_row in selector.xpath(
        './/tr[contains(@class,"hrnz-participant")]'
    ):
        starter = parse_starter(starter_row, race_info.get_output_value("distance"))

        race.add_value("race_starters", starter.load_item())

    return race


def parse_starter(selector: Selector, distance: int) -> ItemLoader:
    race_starter = ItemLoader(item=NZRaceStarter())

    starter_info = ItemLoader(item=NZRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("startnumber", './td[@data-label="Book"]')
    starter_info.add_xpath("driver", './td[@data-label="Driver"]')
    starter_info.add_xpath("trainer", './td[@data-label="Trainer"]')

    starter_info.add_value(
        "started",
        not selector.xpath(".//span[@class='scratchedFont']"),
    )

    handicap = 0

    if selector.xpath('./td[@data-label="HCP" and contains(text(),"m")]'):
        handicap = int(
            selector.xpath('./td[@data-label="HCP" and contains(text(),"m")]/text()')
            .get()
            .replace("m", "")
        )

    starter_info.add_value("distance", distance + handicap)

    race_starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=NZHorse())

    horse_info = ItemLoader(item=NZHorseInfo(), selector=selector)

    horse_info.add_xpath("name", './td[@data-label="Name"]')
    horse_info.add_xpath("gender", './td[@data-label="Sex"]')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=NZRegistration(), selector=selector)

    registration.add_value("source", "hrnz")

    registration.add_xpath("name", './td[@data-label="Name"]')
    registration.add_xpath("link", './td[@data-label="Rating"]/a/@href')

    horse.add_value("registrations", registration.load_item())

    race_starter.add_value("horse", horse.load_item())

    return race_starter
