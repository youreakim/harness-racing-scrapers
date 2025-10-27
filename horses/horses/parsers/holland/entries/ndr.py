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
    DutchRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    for row in response.xpath('//div[@id="ndr-search-results"]//li'):
        raceday = parse_raceday(row)

        key = f"{raceday.get_output_value('raceday_info')['date']}_{raceday.get_output_value('raceday_info')['racetrack']}"

        formdata = {
            "action": "do_search",
            "koersdag": f"{raceday.get_output_value('links')[0]['link']}",
            "koersnr": f"{row.xpath('./@data-koersnr').get()}",
            "isAgenda": "0",
            "paard": "false",
        }

        racedays.append(
            {
                "raceday": raceday,
                "key": key,
                "formdata": formdata,
                "date": raceday.get_output_value("raceday_info")["date"],
            }
        )

    return racedays


def parse_raceday_info(response: Response, raceday: ItemLoader) -> None:
    for race_section in response.xpath(
        '//div[contains(@id,"ndr-tab-") and .//span[contains(text(),"Drafsport")]]'
    ):
        race = parse_race(race_section)

        for starter_row in race_section.xpath(".//tr[@data-id]"):
            parse_starter(starter_row, race)

        raceday.add_value("races", race.load_item())


def parse_raceday(selector: Selector) -> ItemLoader:
    raceday = ItemLoader(item=DutchRaceday())

    raceday_info = ItemLoader(item=DutchRacedayInfo(), selector=selector)

    raceday_info.add_xpath("racetrack", './div[@class="ndr-agenda-baan"]')
    raceday_info.add_xpath("date", './div[@class="ndr-agenda-datum"]')

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=DutchRacedayLink(), selector=selector)

    raceday_link.add_value("source", "ndr")

    raceday_link.add_xpath("link", "./@data-koersdag")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(selector: Selector) -> ItemLoader:
    race = ItemLoader(item=DutchRace())

    race_info = ItemLoader(item=DutchRaceInfo(), selector=selector)

    race_info.add_value("status", "entries")

    race_info.add_xpath("racename", ".//h2")
    race_info.add_xpath("racenumber", './/div[@class="ndr-koers-naam"]')
    race_info.add_xpath("conditions", './/span[@class="ndr-koers-omschrijving"]')
    race_info.add_xpath(
        "distance",
        './/span[@class="ndr-koers-datum-baan" and contains(text()," - ")]',
    )
    race_info.add_xpath(
        "startmethod",
        './/span[@class="ndr-koers-datum-baan" and contains(text()," - ")]',
    )
    race_info.add_xpath(
        "gait",
        './/span[@class="ndr-koers-datum-baan" and contains(text()," - ")]',
    )

    race.add_value("race_info", race_info.load_item())

    return race


def parse_starter(selector: Selector, race: ItemLoader) -> None:
    race_starter = ItemLoader(item=DutchRaceStarter())

    starter_info = ItemLoader(item=DutchRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("driver", "./td[2]")
    starter_info.add_xpath("distance", "./td[3]")
    starter_info.add_xpath("startnumber", "./td[4]")

    race_starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=DutchHorse())

    horse_info = ItemLoader(item=DutchHorseInfo(), selector=selector)

    horse_info.add_xpath("name", "./td[1]")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=DutchRegistration(), selector=selector)

    registration.add_value("source", "ndr")

    registration.add_xpath("name", "./td[1]")
    registration.add_xpath("link", "./@data-id")
    registration.add_xpath("registration", "./@data-id")

    horse.add_value("registrations", registration.load_item())

    race_starter.add_value("horse", horse.load_item())

    race.add_value("race_starters", race_starter.load_item())
