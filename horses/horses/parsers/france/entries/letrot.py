import arrow
from horses.items.france import (
    FrenchHorse,
    FrenchHorseInfo,
    FrenchRace,
    FrenchRaceday,
    FrenchRacedayInfo,
    FrenchRacedayLink,
    FrenchRaceInfo,
    FrenchRaceLink,
    FrenchRaceStarter,
    FrenchRaceStarterInfo,
    FrenchRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    for day in response.xpath(
        '//div[contains(@class,"app-container") and .//a[h2 and contains(@href,"programme")]]'
    ):
        if not day.xpath('.//a[@id="race-card-2"]//span[text()="nc"]'):
            raceday, key = parse_raceday(day)

            urls = day.xpath('.//a[@id="race-card-2"]/@href').getall()

            racedays.append({"raceday": raceday, "key": key, "urls": urls})

    return racedays


def parse_raceday(selector) -> tuple[ItemLoader, str]:
    raceday = ItemLoader(item=FrenchRaceday())

    raceday_link = ItemLoader(item=FrenchRacedayLink(), selector=selector)

    raceday_link.add_xpath("link", ".//a[h2]/@href")
    raceday_link.add_value("source", "LeTrot")

    raceday.add_value("links", raceday_link.load_item())

    raceday_info = ItemLoader(item=FrenchRacedayInfo(), selector=selector)

    raceday_info.add_xpath("racetrack", ".//a/h2/text()")
    raceday_info.add_value("status", "startlist")
    raceday_info.add_value("collection_date", arrow.utcnow().format("YYYY-MM-DD"))
    raceday_info.add_value("date", raceday_link.get_output_value("link"))
    raceday_info.add_value("racetrack_code", raceday_link.get_output_value("link"))

    raceday.add_value("raceday_info", raceday_info.load_item())

    key = f'{raceday_info.get_output_value("date")}_{raceday_info.get_output_value("racetrack_code")}'

    return raceday, key


def parse_race(response: Response, raceday: ItemLoader) -> None:
    race = ItemLoader(item=FrenchRace())

    race_info = ItemLoader(
        item=FrenchRaceInfo(),
        selector=response.xpath('//div[@id="race-information"]'),
    )

    race_info.add_value("racenumber", response.url)
    race_info.add_value("racetype", "race")
    race_info.add_value("status", "entries")

    race_info.add_xpath("racename", ".//h1")
    race_info.add_xpath("conditions", './/div[@class="font-normal"]/div[2]')
    race_info.add_xpath("distance", './/div[@class="font-normal"]/div/div[2]')
    race_info.add_xpath("purse", './/div[@class="font-normal"]/div/div[2]')
    race_info.add_xpath("startmethod", './/div[@class="font-normal"]/div/div[2]')
    race_info.add_xpath("monte", './/div[@class="font-normal"]/div/div[1]/@class')

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=FrenchRaceLink())

    race_link.add_value("link", response.url)
    race_link.add_value("source", "letrot")

    race.add_value("links", race_link.load_item())

    for row in response.xpath('//table[@id="raceleaving"]/tbody[1]/tr'):
        race.add_value("race_starters", parse_starter(response, row))

    raceday.add_value("races", race.load_item())


def parse_starter(response: Response, row: Selector) -> dict:
    starter = ItemLoader(item=FrenchRaceStarter())

    starter_info = ItemLoader(item=FrenchRaceStarterInfo(), selector=row)

    starter_info.add_xpath("startnumber", "./td[1]//div[string-length(text()) > 0]")
    starter_info.add_xpath("order", "./td[1]//div[string-length(text()) > 0]")
    starter_info.add_xpath("distance", "./td[5]//div[b or string-length(text()) > 0]")
    starter_info.add_xpath("driver", './td[6]//a[contains(@href,"jockey")]')
    starter_info.add_xpath("trainer", './td[6]//a[contains(@href,"entraineur")]')
    starter_info.add_xpath("started", "./td[1]//div[string-length(text()) > 0]")

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=FrenchHorse(), selector=row)

    horse_info = ItemLoader(item=FrenchHorseInfo(), selector=row)

    horse_info.add_xpath("name", "./td[2]//a")
    horse_info.add_xpath("gender", "./td[4]//div[string-length(text()) > 0]")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=FrenchRegistration(), selector=row)

    registration.add_xpath("name", "./td[2]//a")
    registration.add_xpath("link", "./td[2]//a/@href")

    horse.add_value("registrations", registration.load_item())

    selector = f"//table[@id='originqualifications']/tbody/tr[.//a[contains(@href,'{registration.get_output_value('link')}')]]"

    parse_pedigree(response, horse, selector)

    starter.add_value("horse", horse.load_item())

    return starter.load_item()


def parse_pedigree(response: Response, horse: ItemLoader, selector: str) -> None:
    if response.xpath(f"{selector}/td[3]//a"):
        sire = ItemLoader(item=FrenchHorse(), selector=response.xpath(selector))

        sire_info = ItemLoader(
            item=FrenchHorseInfo(), selector=response.xpath(selector)
        )

        sire_info.add_value("gender", "horse")

        sire_info.add_xpath("name", "./td[3]//a")

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(
            item=FrenchRegistration(), selector=response.xpath(selector)
        )

        sire_registration.add_xpath("name", "./td[3]//a")
        sire_registration.add_xpath("link", "./td[3]//a/@href")

        sire.add_value("registrations", sire_registration.load_item())

        horse.add_value("sire", sire.load_item())

    if response.xpath(f"{selector}/td[4]//a"):
        dam = ItemLoader(item=FrenchHorse(), selector=response.xpath(selector))

        dam_info = ItemLoader(item=FrenchHorseInfo(), selector=response.xpath(selector))

        dam_info.add_value("gender", "mare")

        dam_info.add_xpath("name", "./td[4]//a")

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(
            item=FrenchRegistration(), selector=response.xpath(selector)
        )

        dam_registration.add_xpath("name", "./td[4]//a")
        dam_registration.add_xpath("link", "./td[4]//a/@href")

        dam.add_value("registrations", dam_registration.load_item())

        if response.xpath(f"{selector}/td[5]//a"):
            dam_sire = ItemLoader(item=FrenchHorse(), selector=response.xpath(selector))

            dam_sire_info = ItemLoader(
                item=FrenchHorseInfo(), selector=response.xpath(selector)
            )

            dam_sire_info.add_value("gender", "horse")

            dam_sire_info.add_xpath("name", "./td[5]//a")

            dam_sire.add_value("horse_info", dam_sire_info.load_item())

            dam_sire_registration = ItemLoader(
                item=FrenchRegistration(), selector=response.xpath(selector)
            )

            dam_sire_registration.add_xpath("name", "./td[5]//a")
            dam_sire_registration.add_xpath("link", "./td[5]//a/@href")

            dam_sire.add_value("registrations", dam_sire_registration.load_item())

            dam.add_value("sire", dam_sire.load_item())

        horse.add_value("dam", dam.load_item())
