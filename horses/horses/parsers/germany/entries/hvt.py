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
    GermanRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_selector in response.xpath(
        '//p[@class="historyitem"]/a[contains(@href,"starter")]'
    ):
        raceday = parse_raceday(raceday_selector)

        if raceday is not None:
            key = f"{raceday.get_output_value('raceday_info')['date']}_{raceday.get_output_value('raceday_info')['racetrack_code']}"

            url = f"https://www.hvtonline.de/{raceday.get_output_value('links')[0]['link']}"

            racedays.append({"raceday": raceday, "key": key, "url": url})

    return racedays


def parse_race_links(response: Response) -> list[str]:
    return response.xpath('//div[@class="rightcol"]//a/@href').getall()


def parse_raceday(selector: Selector) -> ItemLoader | None:
    raceday = ItemLoader(item=GermanRaceday())

    raceday_info = ItemLoader(item=GermanRacedayInfo(), selector=selector)

    raceday_info.add_value("country", "germany")
    raceday_info.add_value("status", "entries")
    raceday_info.add_value("collection_date", arrow.utcnow().format("YYYY-MM-DD"))

    raceday_info.add_xpath("racetrack", 'substring-before("./text()", "›")')
    raceday_info.add_xpath("racetrack_code", "./@href")
    raceday_info.add_xpath("date", "./@href")

    if arrow.get(raceday_info.get_output_value("date")) <= arrow.utcnow():
        return None

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=GermanRacedayLink(), selector=selector)

    raceday_link.add_value("source", "hvt")

    raceday_link.add_xpath("link", "./@href")

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(response: Response, raceday: ItemLoader) -> None:
    race = parse_race_info(response)

    distance = str(race.get_output_value("race_info")["distance"])
    postposition = 1

    for starter_row in response.xpath('//div[@id="cardshort"]/div'):
        if starter_row.xpath("./@class").get() == "band":
            distance = "".join(
                [x for x in starter_row.xpath("./span/text()").get() if x.isnumeric()]
            )
            postposition = 1
            continue

        if not starter_row.xpath("./@class").get():
            continue

        parse_starter(starter_row, race, raceday, postposition, distance)

        postposition += 1

    raceday.add_value("races", race.load_item())


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
        "conditions",
        './/div[@class="racetitleright"]//li[position()=1 or position()=2]',
    )
    race_info.add_xpath(
        "purse", './/li[@class="mittegesamt" and contains(text(),"Dotierung:")]'
    )

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=GermanRaceLink())

    race_link.add_value("link", response.url)
    race_link.add_value("source", "hvt")

    race.add_value("links", race_link.load_item())

    return race


def parse_starter(
    selector: Selector,
    race: ItemLoader,
    raceday: ItemLoader,
    postposition: int,
    distance: str,
) -> None:
    starter = ItemLoader(item=GermanRaceStarter())

    starter_info = ItemLoader(item=GermanRaceStarterInfo(), selector=selector)

    starter_info.add_value("postposition", postposition)
    starter_info.add_value("distance", distance)

    starter_info.add_xpath("startnumber", './/div[@class="startnummer"]')
    starter_info.add_xpath("driver", './/p[@class="row2"]')
    starter_info.add_xpath("trainer", './/p[@class="row4"]')

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=GermanHorse())

    horse_info = ItemLoader(item=GermanHorseInfo(), selector=selector)

    horse_info.add_xpath("name", './/a[@class="callperformances"]')
    horse_info.add_xpath("country", './/a[@class="callperformances"]')
    horse_info.add_xpath("breeder", './/span[@class="item3"]')

    age = selector.xpath('.//td[@class="abstammung"]/text()').get()

    if age:
        age = age[: age.find("j. ")]

        horse_info.add_value(
            "birthdate",
            f'{int(raceday.get_output_value("raceday_info")["date"][:4]) - int(age)}-01-01',
        )

    horse_info.add_xpath("gender", './/td[@class="abstammung"]')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=GermanRegistration(), selector=selector)

    registration.add_value("source", "hvt")

    registration.add_xpath("name", './/a[@class="callperformances"]')
    registration.add_xpath("link", './/a[@class="callperformances"]/@data-horseid')

    horse.add_value("registrations", registration.load_item())

    starter.add_value("horse", horse.load_item())

    race.add_value("race_starters", starter.load_item())
