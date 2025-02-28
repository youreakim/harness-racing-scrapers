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
    FrenchRaceStarterOdds,
    FrenchRaceStarterTime,
    FrenchRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    for day in response.xpath('//div[contains(@class,"app-container") and .//a/h2]'):
        raceday, key = parse_raceday(day)

        race_cards = day.xpath('.//a[@id="race-card-2"]')

        if len(race_cards) == 0:
            continue

        if all(
            card.xpath('.//span[text()="Terminée"]') is not None for card in race_cards
        ):
            urls = [
                f"https://www.letrot.com{card.xpath('./@href').get()}"
                for card in race_cards
            ]

            racedays.append({"raceday": raceday, "key": key, "urls": urls})

    return racedays


def parse_raceday(selector: Selector) -> tuple[ItemLoader, str]:
    raceday = ItemLoader(item=FrenchRaceday())

    raceday_link = ItemLoader(item=FrenchRacedayLink(), selector=selector)

    raceday_link.add_xpath("link", ".//a[h2]/@href")

    raceday_link.add_value("source", "LeTrot")

    raceday.add_value("links", raceday_link.load_item())

    raceday_info = ItemLoader(item=FrenchRacedayInfo(), selector=selector)

    raceday_info.add_xpath("racetrack", ".//a/h2/text()")
    raceday_info.add_value("status", "result")
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
    race_info.add_value("status", "result")

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

    for order, row in enumerate(
        response.xpath('//table[@id="racefinished"]/tbody[1]/tr'), 1
    ):
        race.add_value("race_starters", parse_starter_row(response, row, order))

    raceday.add_value("races", race.load_item())


def parse_starter_row(response: Response, row: Selector, order: int) -> dict:
    starter = ItemLoader(item=FrenchRaceStarter())

    starter_info = ItemLoader(item=FrenchRaceStarterInfo(), selector=row)

    starter_info.add_value("order", order)
    starter_info.add_xpath("started", "./td[1]//div[string-length(text()) > 0]")

    starter_info.add_xpath("trainer", './td[7]//a[contains(@href,"entraineur")]')

    horse = ItemLoader(item=FrenchHorse(), selector=row)

    horse_info = ItemLoader(item=FrenchHorseInfo(), selector=row)

    horse_info.add_xpath("name", "./td[3]//a")
    horse_info.add_xpath("gender", "./td[6]//div[string-length(text()) > 0]")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=FrenchRegistration(), selector=row)

    registration.add_xpath("name", "./td[3]//a")
    registration.add_xpath("link", "./td[3]//a/@href")

    horse.add_value("registrations", registration.load_item())

    if starter_info.get_output_value("started"):
        starter_info.add_xpath(
            "startnumber", './td[2]//div[contains(@class,"absolute")]'
        )
        starter_info.add_xpath(
            "distance", "./td[9]//div[b or string-length(text()) > 0]"
        )
        starter_info.add_xpath("driver", './td[7]//a[contains(@href,"jockey")]')
        starter_info.add_xpath(
            "disqualified", "./td[1]//div[string-length(text()) > 0]"
        )

        if not starter_info.get_output_value("disqualified"):
            starter_info.add_xpath("finish", "./td[1]//div[string-length(text()) > 0]")
            starter_info.add_xpath("purse", './td[12]//div[contains(text(),"€")]')

            starter_time = ItemLoader(item=FrenchRaceStarterTime(), selector=row)

            starter_time.add_value("from_distance", 0)
            starter_time.add_value(
                "to_distance", starter_info.get_output_value("distance")
            )
            starter_time.add_value("time_format", "total")

            starter_time.add_xpath("time", './td[10]//div[contains(text(),"\'")]')

            starter.add_value("times", starter_time.load_item())

            if response.xpath("//table[@id='tracking']"):
                from_distances = [
                    starter_info.get_output_value("distance") - d
                    for d in [2500, 2000, 1500, 1000, 1000, 500]
                ]
                to_distances = [
                    starter_info.get_output_value("distance") - d
                    for d in [2000, 1500, 1000, 500, 0, 0]
                ]

                link = registration.get_output_value("link").split("/")[1]

                for count, column in enumerate(
                    response.xpath(
                        f"//table[@id='tracking']//tr[.//a[contains(@href,'{link}')]]"
                        f"/td[position()>6]"
                    )
                ):
                    if column.xpath(".//p[text()='-']|.//div[text()='-']"):
                        continue

                    starter_time = ItemLoader(
                        item=FrenchRaceStarterTime(), selector=column
                    )

                    starter_time.add_value("from_distance", from_distances[count])
                    starter_time.add_value("to_distance", to_distances[count])
                    starter_time.add_value("time_format", "km")

                    starter_time.add_xpath(
                        "time",
                        ".//span[span]/text()|.//div[contains(text(),'\"')]",
                    )

                    starter.add_value("times", starter_time.load_item())

        starter_odds = ItemLoader(item=FrenchRaceStarterOdds(), selector=row)

        starter_odds.add_value("odds_type", "win")
        starter_odds.add_xpath("odds", "./td[13]//div[string-length(text()) > 0]")

        starter.add_value("odds", starter_odds.load_item())

        starter.add_value("starter_info", starter_info.load_item())

    # pedigree
    parse_pedigree(response, horse, order)

    starter.add_value("horse", horse.load_item())

    return starter.load_item()


def parse_pedigree(response: Response, horse: ItemLoader, order: int) -> None:
    selector = f'//table[@id="originqualifications"]/tbody/tr[{order}]'

    if response.xpath(f"{selector}/td[4]//a"):
        sire = ItemLoader(item=FrenchHorse(), selector=response.xpath(selector))

        sire_info = ItemLoader(
            item=FrenchHorseInfo(), selector=response.xpath(selector)
        )

        sire_info.add_value("gender", "horse")

        sire_info.add_xpath("name", "./td[4]//a")

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(
            item=FrenchRegistration(), selector=response.xpath(selector)
        )

        sire_registration.add_xpath("name", "./td[4]//a")
        sire_registration.add_xpath("link", "./td[4]//a/@href")

        sire.add_value("registrations", sire_registration.load_item())

        horse.add_value("sire", sire.load_item())

    if response.xpath(f"{selector}/td[5]//a"):
        dam = ItemLoader(item=FrenchHorse(), selector=response.xpath(selector))

        dam_info = ItemLoader(item=FrenchHorseInfo(), selector=response.xpath(selector))

        dam_info.add_value("gender", "mare")

        dam_info.add_xpath("name", "./td[5]//a")

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(
            item=FrenchRegistration(), selector=response.xpath(selector)
        )

        dam_registration.add_xpath("name", "./td[5]//a")
        dam_registration.add_xpath("link", "./td[5]//a/@href")

        dam.add_value("registrations", dam_registration.load_item())

        if response.xpath(f"{selector}/td[6]//a"):
            dam_sire = ItemLoader(item=FrenchHorse(), selector=response.xpath(selector))

            dam_sire_info = ItemLoader(
                item=FrenchHorseInfo(), selector=response.xpath(selector)
            )

            dam_sire_info.add_value("gender", "horse")

            dam_sire_info.add_xpath("name", "./td[6]//a")

            dam_sire.add_value("horse_info", dam_sire_info.load_item())

            dam_sire_registration = ItemLoader(
                item=FrenchRegistration(), selector=response.xpath(selector)
            )

            dam_sire_registration.add_xpath("name", "./td[6]//a")
            dam_sire_registration.add_xpath("link", "./td[6]//a/@href")

            dam_sire.add_value("registrations", dam_sire_registration.load_item())

            dam.add_value("sire", dam_sire.load_item())

        horse.add_value("dam", dam.load_item())
