from horses.items.belgium import (
    BelgianHorse,
    BelgianHorseInfo,
    BelgianRace,
    BelgianRaceday,
    BelgianRacedayInfo,
    BelgianRacedayLink,
    BelgianRaceInfo,
    BelgianRaceLink,
    BelgianRaceStarter,
    BelgianRaceStarterInfo,
    BelgianRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_raceday_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_section in response.xpath(
        '//div[contains(@class,"py-2")]/div[position()>1]'
    ):
        post_times = raceday_section.xpath('.//td[@data-title="Tijd"]/text()').getall()

        if len(post_times) == len(set(post_times)):
            raceday = parse_raceday(raceday_section)

            url = f"https://www.trotting.be/races/{raceday.get_output_value('links')[0]['link']}"

            raceday_key = (
                f"{raceday.get_output_value('raceday_info')['date']}_"
                f"{raceday.get_output_value('raceday_info')['racetrack'].replace(' ', '_')}"
            )

            racedays.append(
                {"raceday": raceday, "url": url, "raceday_key": raceday_key}
            )

    return racedays


def parse_races(response: Response, raceday: ItemLoader) -> None:
    for race_section in response.xpath('//div[@class="row" and @id]'):
        race = parse_race(race_section)

        if race is None:
            continue

        for starter_row in race_section.xpath(".//table/tbody/tr"):
            parse_starter(starter_row, race)

            raceday.add_value("races", race.load_item())


def parse_raceday(selector: Selector) -> ItemLoader:
    raceday = ItemLoader(item=BelgianRaceday())

    raceday_info = ItemLoader(item=BelgianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "entries")

    raceday_info.add_xpath("date", ".//h6")
    raceday_info.add_xpath("racetrack", ".//h5")

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=BelgianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "trotting.be")

    raceday_link.add_xpath("link", './/td[@data-title="Naam"]/a/@href')

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(selector: Selector) -> ItemLoader | None:
    race = ItemLoader(item=BelgianRace())

    race_info = ItemLoader(item=BelgianRaceInfo(), selector=selector)

    race_info.add_value("status", "entries")

    race_info.add_xpath("racename", './/div[contains(@class,"card-header")]//h5')

    if "minitrotters" in race_info.get_output_value("racename"):
        return None

    race_info.add_xpath("racenumber", './/span[contains(@class,"race-number-badge")]')
    race_info.add_xpath("racetype", './/div[strong[contains(text(),"Definitie")]]')
    race_info.add_xpath(
        "distance",
        './/strong[contains(text(),"Definitie")]/following-sibling::text()',
    )
    race_info.add_xpath(
        "startmethod",
        './/strong[contains(text(),"Definitie")]/following-sibling::text()',
    )
    race_info.add_xpath(
        "purse",
        './/strong[contains(text(),"Prijzengeld")]/following-sibling::text()',
    )
    race_info.add_xpath(
        "conditions",
        './/strong[contains(text(),"Koersuitschrijvingen")]/following-sibling::text()',
    )
    race_info.add_xpath(
        "conditions",
        './/strong[contains(text(),"Voorwaarden recul")]/following-sibling::text()',
    )

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=BelgianRaceLink(), selector=selector)

    race_link.add_value("source", "trotting.be")

    race_link.add_xpath("link", "./@id")

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(selector: Selector, race: ItemLoader) -> None:
    starter = ItemLoader(item=BelgianRaceStarter())

    starter_info = ItemLoader(item=BelgianRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("startnumber", './td[@data-title="Rugnummer"]')
    starter_info.add_xpath("distance", './td[@data-title="Afstand"]')
    starter_info.add_xpath("driver", './td[@data-title="Jockey"]/text()')

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=BelgianHorse())

    horse_info = ItemLoader(item=BelgianHorseInfo(), selector=selector)

    horse_info.add_xpath("name", './td[@data-title="Paard"]/a')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=BelgianRegistration(), selector=selector)

    registration.add_value("source", "trotting.be")

    registration.add_xpath("name", './td[@data-title="Paard"]/a')
    registration.add_xpath("link", './td[@data-title="Paard"]/a/@href')

    horse.add_value("registrations", registration.load_item())

    starter.add_value("horse", horse.load_item())

    race.add_value("race_starters", starter.load_item())
