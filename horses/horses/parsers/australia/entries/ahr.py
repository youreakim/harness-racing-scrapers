import arrow
from horses.items.australia import (
    AustralianHorse,
    AustralianHorseInfo,
    AustralianRace,
    AustralianRaceday,
    AustralianRacedayInfo,
    AustralianRacedayLink,
    AustralianRaceInfo,
    AustralianRaceLink,
    AustralianRaceStarter,
    AustralianRaceStarterInfo,
    AustralianRegistration,
)
from itemloaders import ItemLoader
from parsel.selector import Selector
from scrapy.http.response import Response


def parse_raceday_calendar(response: Response) -> list[dict]:
    racedays = []

    for tab in response.xpath('//div[@class="tab-content"]/div'):
        race_type = "qualifier" if tab.attrib["id"] == "trials" else "race"

        for raceday_row in tab.xpath('.//tr[td/a[contains(@href,"mc=")]]'):
            raceday = parse_raceday(raceday_row)

            if arrow.utcnow() < arrow.get(
                raceday.get_output_value("raceday_info")["date"]
            ):
                handler = {
                    "raceday": raceday,
                    "url": f"https://www.harness.org.au/racing/fields/"
                    f"race-fields/?mc={raceday.get_output_value('links')[0]['link']}",
                    "race_type": race_type,
                    "raceday_key": f"{raceday.get_output_value('raceday_info')['date']}_"
                    f"{raceday.get_output_value('raceday_info')['racetrack'].replace(' ', '_')}",
                }

                racedays.append(handler)

    return racedays


def parse_raceday(raceday_row: Selector) -> ItemLoader:
    raceday = ItemLoader(item=AustralianRaceday())

    raceday_link = ItemLoader(item=AustralianRacedayLink(), selector=raceday_row)

    raceday_link.add_value("source", "ahr")

    raceday_link.add_xpath("link", "./td[1]/a/@href")

    raceday.add_value("links", raceday_link.load_item())

    raceday_info = ItemLoader(item=AustralianRacedayInfo(), selector=raceday_row)

    raceday_info.add_value("status", "entries")
    raceday_info.add_value("country", "australia")
    raceday_info.add_value("collection_date", arrow.utcnow().format("YYYY-MM-DD"))
    raceday_info.add_value("date", raceday_link.get_output_value("link"))

    raceday_info.add_xpath("racetrack", "./td[1]/a")

    raceday.add_value("raceday_info", raceday_info.load_item())

    return raceday


def parse_races(response: Response, raceday: ItemLoader, race_type: str) -> None:
    for race_table in response.xpath('//div[@id="fields"]'):
        race = parse_race(race_table, race_type)

        for starter_row in race_table.xpath(
            './/table[@class="raceFieldTable"]//tr[td[3]/a]'
        ):
            distance = race.get_output_value("race_info")["distance"]

            race.add_value("race_starters", parse_starter(starter_row, distance))

        raceday.add_value("races", race.load_item())


def parse_race(selector: Selector, race_type: str) -> ItemLoader:
    race = ItemLoader(item=AustralianRace())

    race_info = ItemLoader(item=AustralianRaceInfo(), selector=selector)

    race_info.add_value("status", "entries")
    race_info.add_value("racetype", race_type)

    race_info.add_xpath("racenumber", './/td[contains(@class,"raceNumber")]')
    race_info.add_xpath("racename", './/td[@class="raceTitle"]')
    race_info.add_xpath("distance", './/td[@class="distance"]')
    race_info.add_xpath(
        "conditions",
        './/span[contains(@class,"text-muted")]/@data-original-title',
    )
    race_info.add_xpath("purse", './/td[@class="raceInformation"]')
    race_info.add_xpath("startmethod", './/td[@class="raceInformation"]')
    race_info.add_xpath("gait", './/td[@class="raceInformation"]')

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=AustralianRaceLink(), selector=selector)

    race_link.add_value("source", "ahr")

    race_link.add_xpath("link", "./a/@name")

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(selector: Selector, distance: int) -> dict:
    starter = ItemLoader(item=AustralianRaceStarter())

    starter_info = ItemLoader(item=AustralianRaceStarterInfo(), selector=selector)

    starter_info.add_value("distance", distance)

    starter_info.add_xpath("distance", './td[@class="hcp" and contains(text(),"m")]')
    # distance += int(
    #     selector.xpath('./td[@class="hcp"]/text()')
    #     .get()
    #     .replace("m", "")
    #     .replace("-", "")
    # )

    starter_info.add_xpath("startnumber", './td[@class="horse_number"]')
    starter_info.add_xpath("driver", './td[@class="driver"]/a')
    starter_info.add_xpath("trainer", './td[@class="trainer"]/a')
    starter_info.add_xpath("postposition", './td[@class="hcp"]')

    if selector.xpath('./td[text()="SCRATCHED"]'):
        starter_info.add_value("started", False)
    else:
        starter_info.add_value("started", True)

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=AustralianHorse())

    horse_info = ItemLoader(item=AustralianHorseInfo(), selector=selector)

    horse_info.add_xpath("name", './/a[@class="horse_name_link"]')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=AustralianRegistration(), selector=selector)

    registration.add_value("source", "ahr")

    registration.add_xpath("name", './/a[@class="horse_name_link"]')
    registration.add_xpath("link", './/a[@class="horse_name_link"]/@href')

    horse.add_value("registrations", registration.load_item())

    starter.add_value("horse", horse.load_item())

    return starter.load_item()
