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
    AustralianRaceStarterOdds,
    AustralianRaceStarterTime,
    AustralianRaceTime,
    AustralianRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_raceday_calendar(response: Response) -> list[dict]:
    racedays = []

    for tab in response.xpath('//div[@class="tab-content"]/div'):
        # race_type = "qualifier" if tab.attrib["id"] == "trials" else "race"

        for row in tab.xpath('.//tr[td[1]/a[contains(@href,"mc=")]]'):
            raceday = parse_raceday(row, response.url)

            url = (
                f"https://www.harness.org.au/racing/fields/"
                f"race-fields/?mc={raceday.get_output_value('links')[0]['link']}"
            )

            raceday_key = (
                f"{raceday.get_output_value('raceday_info')['date']}_"
                f"{raceday.get_output_value('raceday_info')['racetrack'].replace(' ', '_')}"
            )

            handler = {
                "raceday": raceday,
                "url": url,
                # "race_type": race_type,
                "raceday_key": raceday_key,
            }

            racedays.append(handler)

    return racedays


def parse_raceday(selector: Selector, date_string: str) -> ItemLoader:
    raceday = ItemLoader(item=AustralianRaceday())

    raceday_info = ItemLoader(item=AustralianRacedayInfo(), selector=selector)

    raceday_info.add_value("date", date_string)
    raceday_info.add_value("country", "australia")
    raceday_info.add_value("status", "result")
    raceday_info.add_value("collection_date", arrow.utcnow().date().isoformat())

    raceday_info.add_xpath("racetrack", "./td[1]/a")

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=AustralianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "ahr")

    raceday_link.add_xpath("link", "./td[1]/a/@href")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(selector: Selector) -> tuple[ItemLoader, ItemLoader]:
    race = ItemLoader(item=AustralianRace())

    race_info = ItemLoader(item=AustralianRaceInfo(), selector=selector)

    race_info.add_value("status", "result")

    race_info.add_xpath("racetype", ".//td[contains(@class,'raceNumber')]/@class")
    race_info.add_xpath("racenumber", './/td[contains(@class,"raceNumber")]')
    race_info.add_xpath("racename", './/td[@class="raceTitle"]')
    race_info.add_xpath("distance", './/td[@class="distance"]')
    race_info.add_xpath(
        "conditions",
        './/span[contains(@class,"text-muted")]/@data-original-title',
    )
    race_info.add_xpath("purse", './td[@class="raceInformation"]')
    race_info.add_xpath("startmethod", './td[@class="raceInformation"]')
    race_info.add_xpath("gait", './/td[@class="raceInformation"]')

    # race.add_value("race_info", race_info.load_item())

    race_link_racing = ItemLoader(item=AustralianRaceLink(), selector=selector)

    race_link_racing.add_value("source", "ahr")

    race_link_racing.add_xpath("link", "./a/@name")

    race.add_value("links", race_link_racing.load_item())

    race_link_breed = ItemLoader(item=AustralianRaceLink())

    race_link_breed.add_value("source", "ab")
    race_link_breed.add_value("link", race_link_racing.get_output_value("link"))

    race.add_value("links", race_link_breed.load_item())

    return race, race_info


def parse_starter(
    selector: Selector, order: int, distance: int
) -> tuple[ItemLoader, ItemLoader, ItemLoader]:
    starter = ItemLoader(item=AustralianRaceStarter())

    starter_info = ItemLoader(item=AustralianRaceStarterInfo(), selector=selector)

    starter_info.add_value("started", True)
    starter_info.add_value("order", order)

    starter_info.add_value("distance", distance)

    starter_info.add_xpath("distance", "./td[@class='hcp' and contains(text(),'m')]")
    # if selector.xpath('./td[@class="hcp" and contains(text(),"m")]'):
    #     distance += int(
    #         selector.xpath('./td[@class="hcp"]/text()')
    #         .get()
    #         .replace("m", "")
    #         .replace("-", "")
    #     )

    starter_info.add_xpath("finish", './td[@class="horse_number"][1]')
    starter_info.add_xpath("finished", './td[@class="horse_number"][1]')
    starter_info.add_xpath("disqualified", './td[@class="horse_number"][1]')
    starter_info.add_xpath("purse", './td[contains(@class,"prizemoney")]')
    starter_info.add_xpath("postposition", './td[@class="barrier"]')
    starter_info.add_xpath("startnumber", './td[@class="horse_number"][last()]')
    starter_info.add_xpath("trainer", './td[contains(@class,"trainer")]')
    starter_info.add_xpath("driver", './td[contains(@class,"driver")]')
    starter_info.add_xpath("margin", './td[@class="margin"]')
    starter_info.add_xpath(
        "comment",
        './td[@class="stewards_comments"]/span/@data-original-title',
    )
    starter_info.add_xpath(
        "gallop",
        './td[@class="stewards_comments"]/span/@data-original-title',
    )

    starter_odds = ItemLoader(item=AustralianRaceStarterOdds(), selector=selector)

    starter_odds.add_value("odds_type", "win")

    starter_odds.add_xpath("odds", './td[contains(@class,"starting_price")]')

    starter.add_value("odds", starter_odds.load_item())

    horse = ItemLoader(item=AustralianHorse())

    horse_info = ItemLoader(AustralianHorseInfo(), selector=selector)

    horse_info.add_xpath("name", './/a[@class="horse_name_link"]')

    starter.add_value("starter_info", starter_info.load_item())

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=AustralianRegistration(), selector=selector)

    registration.add_value("source", "ahr")

    registration.add_xpath("name", './/a[@class="horse_name_link"]')
    registration.add_xpath("link", './/a[@class="horse_name_link"]/@href')

    horse.add_value("registrations", registration.load_item())

    return starter, horse, horse_info


def parse_scratched_starter(
    selector: Selector, scratch_order: int
) -> tuple[ItemLoader, ItemLoader]:
    starter = ItemLoader(item=AustralianRaceStarter())

    starter_info = ItemLoader(item=AustralianRaceStarterInfo(), selector=selector)

    starter_info.add_value("started", False)
    starter_info.add_value("order", scratch_order)

    starter_info.add_xpath("startnumber", './td[@class="number"]')

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=AustralianHorse())

    horse_info = ItemLoader(item=AustralianHorseInfo(), selector=selector)

    horse_info.add_xpath("name", "./td[1]")

    horse.add_value("horse_info", horse_info.load_item())

    return starter, horse


def parse_races(response: Response, handler) -> list[str]:
    urls = []

    for race_table in response.xpath('//div[@id="results"]'):
        race, race_info = parse_race(race_table)

        if race_info.get_output_value("racetype") == "race":
            url = (
                f"https://www.harness.org.au/ausbreed/reports/race_results.cfm"
                f"?race_code={race.get_output_value('links')[0]['link']}"
            )

            urls.append(url)
        order = 1

        for order, starter_row in enumerate(
            race_table.xpath(
                './/table[contains(@class,"resultTable")]//tr[td[@class="horse_number"]]'
            ),
            1,
        ):
            distance = race_info.get_output_value("distance")

            starter, horse, horse_info = parse_starter(starter_row, order, distance)

            if starter.get_output_value("starter_info")["finish"] == 1:
                horse_info.add_xpath(
                    "breeder",
                    './following-sibling::tr/td[@class="horseOwner"]/text()[contains(.,"Breeder(s):")]',
                )

                starter_time = ItemLoader(
                    item=AustralianRaceStarterTime(),
                    selector=race_table.xpath('.//table[@class="raceTimes"]'),
                )

                starter_time.add_value("time_format", "total")
                starter_time.add_value("from_distance", 0)
                starter_time.add_value(
                    "to_distance",
                    starter.get_output_value("starter_info")["distance"],
                )

                starter_time.add_xpath(
                    "time",
                    './/td/strong[text()="Gross Time:"]/following-sibling::text()',
                )

                starter.add_value("times", starter_time.load_item())

            horse.add_value("horse_info", horse_info.load_item())

            handler.add_starter(
                race.get_output_value("links")[0]["link"], starter, horse
            )
            # starters.append({'starter': starter, 'horse': horse, 'started': True})

        for scratch_order, scratch_row in enumerate(
            race_table.xpath('.//tr[td[@class="number"]]'), order + 1
        ):
            starter, horse = parse_scratched_starter(scratch_row, scratch_order)

            handler.add_starter(
                race.get_output_value("links")[0]["link"], starter, horse
            )
            # starters.append({'starter': starter, 'horse': horse, 'started': False})

        parse_race_times(race_table, race, race_info)

        handler.add_race(race, race_info)

    return urls


def parse_race_times(
    selector: Selector, race: ItemLoader, race_info: ItemLoader
) -> None:
    distance_titles = [
        "Lead Time",
        "First Quarter",
        "Second Quarter",
        "Third Quarter",
    ]

    for count, title in enumerate(distance_titles):
        if selector.xpath(f'.//strong[contains(text(),"{title}:")]'):
            q_time = ItemLoader(
                item=AustralianRaceTime(),
                selector=selector.xpath('.//table[@class="raceTimes"]'),
            )

            q_time.add_xpath(
                "time",
                f'.//td/strong[contains(text(),"{title}:")]/following-sibling::text()',
            )

            if q_time.get_output_value("time") == 0:
                continue

            if len(race.get_output_value("race_times")) > 0:
                q_time.add_value(
                    "time", race.get_output_value("race_times")[-1]["time"]
                )

            q_time.add_value(
                "at_distance",
                race_info.get_output_value("distance") - (1609 * (4 - count) / 4),
            )

            q_time.add_value("time_format", "total")

            race.add_value("race_times", q_time.load_item())
