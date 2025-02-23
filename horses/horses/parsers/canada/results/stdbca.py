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
    CanadianRaceStarterOdds,
    CanadianRaceStarterPosition,
    CanadianRaceStarterTime,
    CanadianRaceTime,
    CanadianRegistration,
)
from itemloaders import ItemLoader
from w3lib.html import remove_tags


def parse_races(response, raceday, races, starters):
    racetype = "qualifier" if response.xpath("//h2") else "race"

    for pre in response.xpath("//pre"):
        a_names = pre.xpath("./a/@name").getall()
        hrs = int(float(pre.xpath("count(./hr)").get()))

        for pos, a_name in enumerate(a_names):
            if hrs < len(a_names):
                hr_number = hrs - pos if pos < hrs else 0
            else:
                hr_number = hrs - pos

            # we want all nodes that follows an a tag with a name attribute of N1, N2, ...
            # and precedes the following hr
            # there is usually two pre sections on the result page
            # in the first there is no hr after the last race
            # this will select everything between those two
            selector = f'//pre/node()[preceding-sibling::a[@name="{a_name}"] and count(following-sibling::hr)={hr_number}]'

            race_section = remove_tags(
                "".join(node for node in pre.xpath(selector).getall())
            )

            odds_by_horse = parse_odds(race_section)

            race = races[int(a_name[1:])]["race"]
            race_info = races[int(a_name[1:])]["race_info"]

            parse_race_header(race_section, race, race_info, a_name, racetype)

            parse_race_times(race_section, race)

            result_section = race_section[
                race_section.find("\n", race_section.find("HV PP"))
                + 1 : race_section.find("Time:")
            ].strip()

            for order, starter_row in enumerate(result_section.split("\n"), 1):
                parse_race_starter(starter_row, order, starters, race, odds_by_horse)

            raceday.add_value("races", race.load_item())


def parse_starters(response):
    starters = []

    for starter_section in response.xpath(
        '//details[@data-drupal-selector="edit-results"]//div[@data-racing-key]'
    ):
        horse = parse_starter(starter_section)

        for raceday_section in starter_section.xpath(
            ".//div[@class='racing-result-item']"
        ):
            raceday = parse_raceday(raceday_section)

            race, race_info = parse_race(raceday_section)

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


def parse_starter_section(raceday_section):
    starter_info = ItemLoader(item=CanadianRaceStarterInfo(), selector=raceday_section)

    starter_info.add_xpath("driver", './/a[contains(@href,"type=D")]')
    starter_info.add_xpath("trainer", './/a[contains(@href,"type=T")]')

    return starter_info


def parse_starter(selector):
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


def parse_raceday(selector):
    raceday = ItemLoader(item=CanadianRaceday())

    raceday_info = ItemLoader(item=CanadianRacedayInfo(), selector=selector)

    raceday_info.add_value("status", "results")

    raceday_info.add_xpath("racetrack", './/a[contains(@href,"/results/")]')
    raceday_info.add_xpath("date", './/a[contains(@href,"/results/")]')

    raceday.add_value("raceday_info", raceday_info.load_item())

    raceday_link = ItemLoader(item=CanadianRacedayLink(), selector=selector)

    raceday_link.add_value("source", "stdbca")

    raceday_link.add_xpath("link", './/a/@href[contains(.,"/results/")]')

    raceday.add_value("links", raceday_link.load_item())

    return raceday


def parse_race(selector):
    race = ItemLoader(item=CanadianRace())

    race_info = ItemLoader(item=CanadianRaceInfo(), selector=selector)

    race_info.add_value("status", "results")

    race_info.add_xpath("racenumber", './/a/@href[contains(.,"/results/")]')

    race_link = ItemLoader(item=CanadianRaceLink(), selector=selector)

    race_link.add_value("source", "stdbca")

    race_link.add_xpath("link", './/a/@href[contains(.,"/results/")]')

    race.add_value("links", race_link.load_item())

    # trackit_link = ItemLoader(item=CanadianRacedayLink())
    #
    # trackit_link.add_value('source', 'trackit')
    # trackit_link.add_value('link',
    #                        f'https://trackit.standardbredcanada.ca/?op=QRR&trk={racetrack}&perf=N&date={DD-MMM-YYYY}&racno={racenumber}')
    #
    # race.add_value('links', trackit_link.load_item())

    return race, race_info


def parse_odds(selector):
    odds_section_rows = selector[
        : selector.find("\n", selector.find(" MILE") - 10)
    ].split("\n")

    odds_by_horse = {}

    if odds_section_rows[1].strip() != "":
        for odds_row in odds_section_rows[1:]:
            if (
                odds_row.strip() != ""
                and odds_row[0].isnumeric()
                and "-" in odds_row[:3]
            ):
                horse_odds = {
                    "name": odds_row[
                        odds_row.find("-") + 1 : odds_row.find(".") - 5
                    ].strip(),
                    "odds": [],
                }

                odds = reversed(
                    [
                        x.strip()
                        for x in odds_row[
                            odds_row.rfind(" ", 0, odds_row.find(".")) : odds_row.find(
                                " ", odds_row.rfind(".")
                            )
                        ].split(" ")
                        if x.strip() != ""
                    ]
                )

                for count, value in enumerate(odds):
                    current = ItemLoader(item=CanadianRaceStarterOdds())

                    current.add_value("odds_type", ["show", "place", "win"][count])
                    current.add_value("odds", value)

                    horse_odds["odds"].append(current.load_item())

                odds_by_horse[odds_row.split("-")[0]] = horse_odds

    return odds_by_horse


def parse_race_header(selector, race, race_info, a_name, racetype):
    race_info.add_value("status", "result")
    race_info.add_value("racenumber", a_name[1:])
    race_info.add_value("startmethod", "mobile")
    race_info.add_value("racetype", racetype)

    race_info_section = selector[
        selector.rfind("\n", 0, selector.find(" MILE")) : selector.find("Last\n")
    ].strip()

    race_info.add_value(
        "distance", race_info_section[: race_info_section.find(" MILE")]
    )
    race_info.add_value("gait", race_info_section.split("\n")[0])

    if ", PURSE $" in race_info_section:
        race_info.add_value(
            "purse",
            race_info_section[
                race_info_section.find("$") + 1 : race_info_section.find("\n")
            ],
        )

    race_info.add_value("conditions", " ".join(race_info_section.split("\n")[1:]))

    race.add_value("race_info", race_info.load_item())


def parse_race_times(selector, race):
    time_distances = [1609 / 4, 1609 / 2, 1609 * 3 / 4, 1609]

    time_string = selector[
        selector.find("Time:") + 5 : selector.find("\n", selector.find("Time:"))
    ]

    if "(" in time_string:
        time_string = time_string[: time_string.find("(")]

    for count, time in enumerate(time_string.strip().split(", ")):
        race_time = ItemLoader(item=CanadianRaceTime())

        race_time.add_value("time", time)
        race_time.add_value("at_distance", time_distances[count])

        race.add_value("race_times", race_time.load_item())


def parse_race_starter(selector, order, starters, race, odds_by_horse):
    race_info = race.get_output_value("race_info")

    horse_name = selector[4:28]

    if "(" in horse_name:
        horse_name = horse_name[: horse_name.find("(")]

    key = "".join(x for x in horse_name if x.isalpha()).upper()

    starter = starters[race_info["racenumber"]][key]["starter"]

    starter_info = starters[race_info["racenumber"]][key]["starter_info"]

    starter_info.add_value("order", order)
    starter_info.add_value("startnumber", selector[:4])
    starter_info.add_value("distance", race_info["distance"])

    if "SCRATCHED" in selector:
        starter_info.add_value("started", False)

    else:
        starter_info.add_value("started", True)
        starter_info.add_value("postposition", selector[32:37])
        starter_info.add_value("finish", selector[70:80])
        starter_info.add_value("gallop", "X" in selector[32:80])

        for start, end in [(81, 88), (89, 93)]:
            starter_time = ItemLoader(item=CanadianRaceStarterTime())

            starter_time.add_value("time_format", "total")

            from_distance = (
                0
                if start == 81
                else round(starter_info.get_output_value("distance") - 1609 / 4)
            )
            starter_time.add_value("from_distance", from_distance)

            starter_time.add_value(
                "to_distance", starter_info.get_output_value("distance")
            )

            starter_time.add_value("time", selector[start:end])

            starter.add_value("times", starter_time.load_item())

        if len(odds_by_horse) != 0:
            horse_odds = odds_by_horse.get(
                str(starter_info.get_output_value("startnumber"))
            )

            if starter_info.get_output_value("finish") != 1:
                starter_odds = ItemLoader(item=CanadianRaceStarterOdds())

                starter_odds.add_value("odds_type", "win")
                starter_odds.add_value(
                    "odds",
                    selector[selector.rfind(".") - 3 : selector.rfind(".") + 3],
                )

                starter.add_value("odds", starter_odds.load_item())

            if horse_odds:
                starter.add_value("odds", horse_odds["odds"])

        position_values = [
            (37, 45, "1/4"),
            (45, 53, "1/2"),
            (53, 61, "3/4"),
            (61, 69, "stretch"),
        ]

        for start_index, end_index, at_distance in position_values:
            position = ItemLoader(item=CanadianRaceStarterPosition())

            position.add_value("position", selector[start_index:end_index])
            position.add_value("at_distance", at_distance)

            starter.add_value("positions", position.load_item())

        starter_info.add_value(
            "finished",
            "PU" in selector[32:80] or "FELL" in selector[32:80],
        )

    starter.add_value("starter_info", starter_info.load_item())

    horse = starters[race_info["racenumber"]][key]["horse"]

    horse_info = ItemLoader(item=CanadianHorseInfo())

    horse_info.add_value("name", horse_name)

    horse.add_value("horse_info", horse_info.load_item())

    starter.add_value("horse", horse.load_item())

    race.add_value("race_starters", starter.load_item())
