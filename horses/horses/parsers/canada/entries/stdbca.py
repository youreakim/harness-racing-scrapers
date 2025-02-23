import arrow
from horses.items.canada import (
    CanadianHorse,
    CanadianHorseInfo,
    CanadianRace,
    CanadianRaceday,
    CanadianRacedayInfo,
    CanadianRacedayLink,
    CanadianRaceInfo,
    CanadianRaceLink,
    CanadianRaceStarter,
    CanadianRaceStarterInfo,
    CanadianRegistration,
)
from itemloaders import ItemLoader
from w3lib.html import remove_tags


def parse_starters(response):
    starters = []

    for starter_section in response.xpath(
        '//details[@data-drupal-selector="edit-entries"]//div[@data-racing-key and .//span[text()="*"]]'
    ):
        horse = parse_horse(starter_section)

        for raceday_section in starter_section.xpath(
            ".//div[@class='racing-result-item']"
        ):
            raceday = parse_raceday(raceday_section)

            if (
                arrow.now().date()
                > arrow.get(raceday.get_output_value("raceday_info")["date"]).date()
            ):
                continue

            race, race_info = parse_race_info(raceday_section)

            starter_info = parse_starter_section(raceday_section)

            starters.append(
                {
                    "horse": horse,
                    "raceday": raceday,
                    "race": race,
                    "race_info": race_info,
                    "starter": ItemLoader(item=CanadianRaceStarter()),
                    "starter_info": starter_info,
                }
            )

    return starters


def parse_starter_section(selector):
    starter_info = ItemLoader(item=CanadianRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("driver", './/a[contains(@href,"type=D")]')
    starter_info.add_xpath("trainer", './/a[contains(@href,"type=T")]')

    return starter_info


def parse_raceday(selector):
    raceday = ItemLoader(item=CanadianRaceday())

    raceday_info = ItemLoader(item=CanadianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "entries")

    raceday_info.add_xpath("racetrack", './/a[contains(@href,"/entries/")]')
    raceday_info.add_xpath("date", './/a[contains(@href,"/entries/")]')

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=CanadianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "stdbca")

    raceday_link.add_xpath("link", './/a/@href[contains(.,"/entries/")]')

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race_info(selector):
    race = ItemLoader(item=CanadianRace())

    race_info = ItemLoader(item=CanadianRaceInfo(), selector=selector)

    race_info.add_value("status", "entries")

    race_info.add_xpath("racenumber", './/a/@href[contains(.,"/entries/")]')

    race_link = ItemLoader(item=CanadianRaceLink(), selector=selector)

    race_link.add_value("source", "stdbca")

    race_link.add_xpath("link", './/a/@href[contains(.,"/entries/")]')

    race.add_value("links", race_link.load_item())

    # trackit_link = ItemLoader(item=CanadianRacedayLink())
    #
    # trackit_link.add_value('source', 'trackit')
    # trackit_link.add_value('link',
    #                        f'https://trackit.standardbredcanada.ca/?op=QRR&trk={racetrack}&perf=N&date={DD-MMM-YYYY}&racno={racenumber}')
    #
    # race.add_value('links', trackit_link.load_item())

    return race, race_info


def parse_horse(selector):
    horse = ItemLoader(item=CanadianHorse())

    horse_info = ItemLoader(item=CanadianHorseInfo(), selector=selector)

    horse_info.add_xpath("name", "./h3/span")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=CanadianRegistration(), selector=selector)

    registration.add_value("source", "trackit")

    registration.add_xpath("name", "./h3/span")
    registration.add_xpath("link", "./@data-racing-key")

    horse.add_value("registrations", registration.load_item())

    return horse


def parse_starter(selector):
    starter = ItemLoader(item=CanadianRaceStarter())

    starter_info = ItemLoader(item=CanadianRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("driver", './/a[contains(@href,"type=D")]')
    starter_info.add_xpath("trainer", './/a[contains(@href,"type=T")]')

    return starter, starter_info, parse_horse(selector)


def parse_race_header(selector, race_info, racetype):
    race_info.add_value("status", "entries")
    race_info.add_value("racetype", racetype)
    race_info.add_value("gait", selector.split("\n")[0])
    race_info.add_value("purse", selector.split("\n")[0])
    race_info.add_value("distance", selector.split("\n")[0])
    race_info.add_value("racenumber", selector.split("\n")[0])
    race_info.add_value("conditions", selector[selector.find("\n") + 1 :])
    race_info.add_value("startmethod", "mobile")


def parse_starter_row(selector, starters, race):
    if "AE" not in selector[:5]:
        horse_name = selector[5:34]

        if "(" in horse_name:
            horse_name = horse_name[: horse_name.find("(")].strip()

        key = "".join(x for x in horse_name if x.isalpha())

        s = starters[race.get_output_value("race_info")["racenumber"]][key.upper()]

        starter = s["starter"]
        starter_info = s["starter_info"]
        horse = s["horse"]

        starter_info.add_value("startnumber", selector[:4])

        starter.add_value("horse", horse.load_item())

        starter.add_value("starter_info", starter_info.load_item())

        race.add_value("race_starters", starter.load_item())


def parse_races(response, raceday, races, starters):
    racetype = "qualifier" if response.xpath("//h2") else "race"

    race_splits = [
        item.strip()
        for sublist in [
            remove_tags(x).split("\n\n") for x in response.xpath("//pre").getall()
        ]
        for item in sublist
        if " -- " in item
    ]

    for race_split in race_splits:
        racenumber = int(race_split[: race_split.find("--")].strip())

        r = races[racenumber]

        race = r["race"]
        race_info = r["race_info"]

        search_string = "Post Time:" if "Post Time:" in race_split else "Lasix:"

        header = race_split[: race_split.find(search_string)]
        starter_section = race_split[
            race_split.find("\n", race_split.find(search_string)) + 1 :
        ]

        parse_race_header(header, race_info, racetype)

        race.add_value("race_info", race_info.load_item())

        for starter_row in starter_section.split("\n"):
            if not starter_row[3].isnumeric():
                continue

            parse_starter_row(starter_row, starters, race)

        raceday.add_value("races", race.load_item())
