import arrow
from parsel import Selector
from scrapy.http.response import Response
from horses.items.norway import (
    NorwegianHorse,
    NorwegianHorseInfo,
    NorwegianRace,
    NorwegianRaceday,
    NorwegianRacedayInfo,
    NorwegianRacedayLink,
    NorwegianRaceInfo,
    NorwegianRaceLink,
    NorwegianRaceStarter,
    NorwegianRaceStarterInfo,
    NorwegianRegistration,
)
from itemloaders import ItemLoader


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    for raceday_row in response.xpath("//div[@class='rc-item' and .//a[text()='Startliste']]"):
        raceday = ItemLoader(item=NorwegianRaceday())

        raceday_info = ItemLoader(item=NorwegianRacedayInfo(), selector=raceday_row)

        raceday_info.add_xpath("racetrack", "./div[@class='rc-item__info']")
        raceday_info.add_xpath("date", ".//a[text()='Startliste']/@href")

        raceday_info.add_value("status", "entries")

        raceday.add_value("raceday_info", raceday_info.load_item())

        raceday_date = arrow.get(raceday_info.get_output_value("date")).date()

        if raceday_date <= arrow.utcnow().date():
            continue

        raceday_link = ItemLoader(item=NorwegianRacedayLink(), selector=raceday_row)

        raceday_link.add_xpath("link", ".//a[text()='Startliste']/@href")

        raceday_link.add_value("source", "dnt")

        raceday.add_value("links", raceday_link.load_item())

        key = f"{raceday_info.get_output_value('date')}_{raceday_info.get_output_value('racetrack')}"

        url = raceday_row.xpath(".//a[text()='Startliste']/@href").get()

        racedays.append({"raceday": raceday, "key": key, "url": url})

    return racedays


def parse_raceday(response: Response, raceday: ItemLoader) -> None:
    for race_element in response.xpath("//div[@class='js-tabbedContent-panel']"):
        race = parse_race(race_element, raceday)

        raceday.add_value("races", race.load_item())
 

def parse_race(selector: Selector, raceday: ItemLoader) -> ItemLoader:
    race = ItemLoader(item=NorwegianRace())

    race_info = ItemLoader(item=NorwegianRaceInfo(), selector=selector)

    race_info.add_value("status", "entries")
    race_info.add_value("gait", "trot")

    race_info.add_xpath("racenumber", "(//preceding-sibling::div/@id)[last()]")

    race_info.add_xpath("conditions", "string(./p)")
    race_info.add_xpath("distance", "string(./p)")
    race_info.add_xpath('purse', './p[contains(text(),"Premier:")]')
    race_info.add_xpath("startmethod", "string(./p)")
    race_info.add_xpath("racetype", "string(./p)")
    race_info.add_xpath("monte", "string(./p)")

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=NorwegianRaceLink(), selector=selector)

    race_link.add_value(
        "link",
        f"{raceday.get_output_value('links')[0]['link']}#race-{race.get_output_value('race_info')['racenumber']}",
    )

    race_link.add_value("source", "DNT")

    race.add_value("links", race_link.load_item())

    for starter_element in selector.xpath(".//tbody[.//tr[@class='expandable-row']]"):
        starter = parse_starter(starter_element)

        race.add_value("race_starters", starter.load_item())

    return race


def parse_starter(selector: Selector) -> ItemLoader:
    starter = ItemLoader(item=NorwegianRaceStarter())

    starter_info = ItemLoader(
        item=NorwegianRaceStarterInfo(),
        selector=selector
    )

    starter_info.add_xpath("startnumber", './/td[@class="startNumber"]')
    starter_info.add_xpath("distance", "./tr[1]/td[10]")
    starter_info.add_xpath("driver", "./tr[1]/td[2]")
    starter_info.add_xpath("postposition", "./tr[1]/td[3]")

    starter_info.add_xpath("trainer", './/dt[text()="Trener:"]/following-sibling::dd')

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=NorwegianHorse())

    horse_info = ItemLoader(
        item=NorwegianHorseInfo(),
        selector=selector
    )

    horse_info.add_xpath("name", ".//th/a")
    horse_info.add_xpath("country", ".//th/a")

    horse_info.add_xpath("breeder", './/dt[text()="Oppdretter:"]/following-sibling::dd')
    horse_info.add_xpath("gender", ".//p/text()[position()=1 and contains(.,'-års')]")

    horse_info.add_xpath("breed", "(.//ancestor::div[@class='js-tabbedContent-panel'])[last()]/p")

    age_string = horse_info.selector.xpath("substring-before(.//p/text()[contains(.,'-års')],'-')").get()

    if age_string:
        age = int(age_string.strip())

        horse_info.add_value("birthdate", f"{2025 - age}-01-01")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=NorwegianRegistration(),
        selector=selector
    )

    registration.add_value("source", "DNT")

    registration.add_xpath("name", ".//th/a")
    registration.add_xpath("link", ".//th/a/@href")

    horse.add_value("registrations", registration.load_item())

    sire = ItemLoader(item=NorwegianHorse())

    sire_info = ItemLoader(
        item=NorwegianHorseInfo(),
        selector=selector.xpath('./tr[2]//a[contains(@href,"horse")]'),
    )

    sire_info.add_value("gender", "horse")

    sire_info.add_xpath("name", ".")
    sire_info.add_xpath("country", ".")

    sire.add_value("horse_info", sire_info.load_item())

    sire_registration = ItemLoader(
        item=NorwegianRegistration(),
        selector=selector.xpath('./tr[2]//a[contains(@href,"horse")]'),
    )

    sire_registration.add_value("source", "DNT")

    sire_registration.add_xpath("name", ".")
    sire_registration.add_xpath("link", "./@href")

    sire.add_value("registrations", sire_registration.load_item())

    horse.add_value("sire", sire.load_item())

    dam = ItemLoader(item=NorwegianHorse())

    dam_info = ItemLoader(
        item=NorwegianHorseInfo(),
        selector=selector.xpath('./tr[2]//a[contains(@href,"horse")][2]'),
    )

    dam_info.add_value("gender", "mare")

    dam_info.add_xpath("name", ".")
    dam_info.add_xpath("country", ".")

    dam.add_value("horse_info", dam_info.load_item())

    dam_registration = ItemLoader(
        item=NorwegianRegistration(),
        selector=selector.xpath('./tr[2]//a[contains(@href,"horse")][2]'),
    )

    dam_registration.add_value("source", "DNT")

    dam_registration.add_xpath("name", ".")
    dam_registration.add_xpath("link", "./@href")

    dam.add_value("registrations", dam_registration.load_item())

    dam_sire = ItemLoader(item=NorwegianHorse())

    dam_sire_info = ItemLoader(
        item=NorwegianHorseInfo(),
        selector=selector.xpath('./tr[2]//a[contains(@href,"horse")][3]'),
    )

    dam_sire_info.add_value("gender", "horse")

    dam_sire_info.add_xpath("name", ".")
    dam_sire_info.add_xpath("country", ".")

    dam_sire.add_value("horse_info", dam_sire_info.load_item())

    dam_sire_registration = ItemLoader(
        item=NorwegianRegistration(),
        selector=selector.xpath('./tr[2]//a[contains(@href,"horse")][3]'),
    )

    dam_sire_registration.add_value("source", "DNT")

    dam_sire_registration.add_xpath("name", ".")
    dam_sire_registration.add_xpath("link", "./@href")

    dam_sire.add_value("registrations", dam_sire_registration.load_item())

    dam.add_value("sire", dam_sire.load_item())

    horse.add_value("dam", dam.load_item())

    starter.add_value("horse", horse.load_item())

    return starter
