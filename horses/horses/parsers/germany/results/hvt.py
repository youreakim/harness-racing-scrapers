import arrow
from horses.items.germany import (
    GermanHorse,
    GermanHorseInfo,
    GermanRace,
    GermanRaceday,
    GermanRacedayInfo,
    GermanRacedayLink,
    GermanRaceInfo,
    GermanRaceLink,
    GermanRaceStarter,
    GermanRaceStarterInfo,
    GermanRaceStarterOdds,
    GermanRaceStarterTime,
    GermanRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_row in response.xpath('//table[@class="rboverview"]//a'):
        raceday = parse_raceday(raceday_row)

        raceday_date = arrow.get(
            raceday.get_output_value("raceday_info")["date"], "YYYY-MM-DD"
        ).date()

        key = f"{raceday_date.isoformat()}_{raceday.get_output_value('raceday_info')['racetrack_code']}"

        url = f"https://www.hvtonline.de/{raceday.get_output_value('links')[0]['link']}"

        racedays.append(
            {"raceday": raceday, "key": key, "url": url, "date": raceday_date}
        )

    return racedays


def parse_raceday_links(response: Response) -> list[str]:
    return response.xpath(
        '//div[@class="rbleftcol"]//a/@href[contains(.,"rennbericht")]'
    ).getall()


def parse_race(response: Response, raceday: ItemLoader) -> None:
    race = parse_race_info(response)

    placeodds_string = response.xpath(
        'substring-before(//td[contains(text(),"Platz:")]/following-sibling::td/text(),":")'
    ).get()

    if placeodds_string:
        placeodds = [
            int(x) / 10 for x in placeodds_string.split("-") if x.strip() != ""
        ]

        for order, starter_row in enumerate(
            response.xpath('//table[@class="rbfull"]/tbody/tr[count(td)=8]'), 1
        ):
            parse_starter(starter_row, race, raceday, order, placeodds)

        raceday.add_value("races", race.load_item())


def parse_raceday(selector: Selector) -> ItemLoader:
    raceday = ItemLoader(item=GermanRaceday())

    raceday_info = ItemLoader(item=GermanRacedayInfo(), selector=selector)

    raceday_info.add_value("country", "germany")
    raceday_info.add_value("status", "result")
    raceday_info.add_value("collection_date", arrow.utcnow().date().isoformat())

    raceday_info.add_xpath("racetrack", ".")
    raceday_info.add_xpath("racetrack_code", "./@href")
    raceday_info.add_xpath("date", "./@href")

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=GermanRacedayLink(), selector=selector)

    raceday_link.add_value("source", "hvt")

    raceday_link.add_xpath("link", "./@href")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race_info(response: Response) -> ItemLoader:
    race = ItemLoader(item=GermanRace())

    race_info = ItemLoader(
        item=GermanRaceInfo(),
        selector=response.xpath('//div[@id="raceheaderleft"]'),
    )

    race_info.add_xpath("racenumber", './/div[@class="racetitleleft"]/h3')
    race_info.add_xpath(
        "distance", './/li[@class="mitterechts" and contains(text(),"Distanz:")]'
    )
    race_info.add_xpath(
        "startmethod", './/li[@class="mitterechts" and contains(text(),"Distanz:")]'
    )
    race_info.add_xpath("racetype", './/div[@class="racetitleleft"]/h3')
    race_info.add_xpath("racename", './/h3[@class="fulltext"]')
    race_info.add_xpath(
        "conditions", './/div[@class="racetitleright"]//li[position()=1]'
    )
    race_info.add_xpath(
        "purse", './/li[@class="mittegesamt" and contains(text(),"Dotierung:")]'
    )

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=GermanRaceLink())

    race_link.add_value("source", "hvt")
    race_link.add_value("link", response.url)

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(
    selector: Selector,
    race: ItemLoader,
    raceday: ItemLoader,
    order: int,
    placeodds: list[dict],
) -> None:
    starter = ItemLoader(item=GermanRaceStarter())

    starter_info = ItemLoader(item=GermanRaceStarterInfo(), selector=selector)

    starter_info.add_value("started", True)
    starter_info.add_value("order", order)

    starter_info.add_xpath(
        "finish", './td[@class="racenumber" and string-length(text())>0]'
    )
    starter_info.add_xpath("driver", "./td[3]")
    starter_info.add_xpath("trainer", "./td[4]")
    starter_info.add_xpath("distance", "./td[6]")

    starter_time = ItemLoader(item=GermanRaceStarterTime(), selector=selector)

    starter_time.add_value("from_distance", 0)
    starter_time.add_value("to_distance", starter_info.get_output_value("distance"))
    starter_time.add_value("time_format", "total")

    starter_time.add_xpath("time", "./td[5]")

    starter.add_value("times", starter_time.load_item())

    if race.get_output_value("race_info")["racetype"] == "race":
        starter_odds = ItemLoader(item=GermanRaceStarterOdds(), selector=selector)

        starter_odds.add_value("odds_type", "win")

        starter_odds.add_xpath("odds", "./td[8]")

        starter.add_value("odds", starter_odds.load_item())

        if order <= len(placeodds):
            place_odds = ItemLoader(item=GermanRaceStarterOdds())

            place_odds.add_value("odds_type", "show")
            place_odds.add_value("odds", placeodds[order - 1])

            starter.add_value("odds", place_odds.load_item())

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=GermanHorse())

    horse_info = ItemLoader(item=GermanHorseInfo(), selector=selector)

    horse_info.add_xpath("name", "./td[2]/strong")
    horse_info.add_xpath("country", "./td[2]/strong")

    horse_info.selector = selector.xpath("./following-sibling::tr[1]")

    horse_info.add_xpath("breeder", "./td[3]")
    horse_info.add_xpath("gender", "./td[1]")

    age = selector.xpath("./following-sibling::tr[1]/td[1]/text()").get()

    if age:
        horse_info.add_value(
            "birthdate",
            int(raceday.get_output_value("raceday_info")["date"][:4])
            - int(age[: age.find("j. ")]),
        )

    horse.add_value("horse_info", horse_info.load_item())

    starter.add_value("horse", horse.load_item())

    race.add_value("race_starters", starter.load_item())
