import arrow
import re
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
    NorwegianRaceStarterOdds,
    NorwegianRaceStarterTime,
    NorwegianRegistration,
)
from itemloaders import ItemLoader


def parse_calendar(
    response: Response,
    start_date: arrow.arrow.Arrow,
    end_date: arrow.arrow.Arrow
) -> list[dict]:
    racedays = []

    for raceday_row in response.xpath("//div[@class='rc-item' and .//a[text()='Resultater']]"):
        raceday = ItemLoader(item=NorwegianRaceday())

        raceday_info = ItemLoader(item=NorwegianRacedayInfo(), selector=raceday_row)

        raceday_info.add_xpath("racetrack", "./div[@class='rc-item__info']")
        raceday_info.add_xpath("date", ".//a[text()='Resultater']/@href")

        raceday_info.add_value("status", "entries")

        raceday.add_value("raceday_info", raceday_info.load_item())

        raceday_date = arrow.get(raceday_info.get_output_value("date")).date()

        if start_date.date() > raceday_date or raceday_date > end_date.date():
            continue

        raceday_link = ItemLoader(item=NorwegianRacedayLink(), selector=raceday_row)

        raceday_link.add_xpath("link", ".//a[text()='Resultater']/@href")

        raceday_link.add_value("source", "dnt")

        raceday.add_value("links", raceday_link.load_item())

        key = f"{raceday_info.get_output_value('date')}_{raceday_info.get_output_value('racetrack')}"

        url = raceday_row.xpath(".//a[text()='Resultater']/@href").get()

        racedays.append({"raceday": raceday, "key": key, "url": url})

    return racedays


def parse_raceday(response: Response, raceday: ItemLoader) -> None:
    for race_element in response.xpath("//div[contains(@class,'js-tabbedContent-panel')]"):
        race = parse_race(race_element, raceday)

        raceday.add_value("races", race.load_item())


def parse_race(selector: Selector, raceday: ItemLoader) -> ItemLoader:
    race = ItemLoader(item=NorwegianRace())

    race_info = ItemLoader(item=NorwegianRaceInfo(), selector=selector)

    race_info.add_value("status", "result")
    race_info.add_value("gait", "trot")

    race_info.add_xpath("conditions", "./div/p")
    race_info.add_xpath("distance", "./div/p")
    race_info.add_xpath("purse", "./div/p")
    race_info.add_xpath("startmethod", "./div/p")
    race_info.add_xpath("racetype", "./div/p")
    race_info.add_xpath("monte", "./div/p")
    race_info.add_xpath("racenumber", "./@id")

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=NorwegianRaceLink(), selector=selector)

    race_link.add_value(
        "link",
        f"{raceday.get_output_value('links')[0]['link']}"\
        f"#race-{race_info.get_output_value('racenumber')}"
    )
    race_link.add_value("source", "DNT")

    race.add_value("links", race_link.load_item())

    odds = {"win": [], "show": []}

    if race_info.get_output_value("racetype") == "race":
        win_odds = selector.xpath(
            "substring-after(.//table[@class='table']//td/text()[contains(.,',') and starts-with(.,'V: ')],'V:')"
        ).get()

        odds["win"] = [float(x.strip().replace(",", ".")) for x in re.split("-|/", win_odds)]

        show_odds= selector.xpath(
            "substring-after(.//table[@class='table']//td/text()[contains(.,',') and starts-with(.,'P: ')],'P:')"
        ).get()

        odds["show"] = [float(x.strip().replace(",", ".")) for x in re.split("-|/", show_odds)]

    for order, starter_section in enumerate(
        selector.xpath('./div[@class="table-wrapper"]//tbody'), 1
    ):
        starter = parse_starter(starter_section, order, race, odds)

        race.add_value("race_starters", starter.load_item())

    return race


def parse_starter(
    selector: Selector,
    order: int,
    race: ItemLoader,
    odds: dict[str, list]
) -> ItemLoader:
    starter = ItemLoader(item=NorwegianRaceStarter())

    starter_info = ItemLoader(
        item=NorwegianRaceStarterInfo(),
        selector=selector.xpath("./tr[1]"),
    )

    starter_info.add_value("order", order)

    starter_info.add_value(
        "started",
        selector.xpath("./tr[1]/@class").get() != "scratched",
    )
    starter_info.add_xpath("startnumber", "./td[2]")
    starter_info.add_xpath("distance", "./td[3]")
    starter_info.add_xpath("driver", "./td[7]")

    if starter_info.get_output_value("started"):
        starter_info.add_xpath("disqualified", "./td[1]")
        starter_info.add_xpath("finish", "./td[1]")
        starter_info.add_xpath("gallop", "./td[4]")
        starter_info.add_xpath("finished", "./td[5]")

        if race.get_output_value("race_info")["racetype"] == "race":
            starter_info.add_xpath("purse", "./td[6]")

            if order <= len(odds["win"]):
                win_odds = ItemLoader(item=NorwegianRaceStarterOdds())

                win_odds.add_value("odds_type", "win")
                win_odds.add_value("odds", odds["win"][order - 1])

                starter.add_value("odds", win_odds.load_item())

            if order <= len(odds["show"]):
                show_odds = ItemLoader(item=NorwegianRaceStarterOdds())

                show_odds.add_value("odds_type", "show")
                show_odds.add_value("odds", odds["show"][order - 1])

                starter.add_value("odds", show_odds.load_item())

        if not starter_info.get_output_value(
            "disqualified"
        ) and starter_info.get_output_value("finished"):
            starter_time = ItemLoader(
                item=NorwegianRaceStarterTime(),
                selector=selector.xpath("./tr[1]"),
            )

            starter_time.add_value("from_distance", 0)
            starter_time.add_value(
                "to_distance", starter_info.get_output_value("distance")
            )
            starter_time.add_value("time_format", "total")

            starter_time.add_xpath("time", "./td[4]")

            starter.add_value("times", starter_time.load_item())

    horse = ItemLoader(item=NorwegianHorse())

    horse_info = ItemLoader(
        item=NorwegianHorseInfo(),
        selector=selector
    )

    horse_info.add_xpath("name", ".//th/strong/a")
    horse_info.add_xpath("country", ".//th/strong/a")

    if selector.xpath("./@class").get() == "winner":
        starter_info.add_xpath(
            "trainer", './/following-sibling::tr//strong[text()="Trener:"]/following-sibling::a'
        )

        horse_info.add_xpath(
            "breeder",
            './/following-sibling::tr//strong[text()="Oppdretter:"]/following-sibling::text()',
        )

        sire = ItemLoader(item=NorwegianHorse())

        sire_info = ItemLoader(
            item=NorwegianHorseInfo(),
            selector=selector.xpath("./tr[2]"),
        )

        sire_info.add_value("gender", "horse")

        sire_info.add_xpath("name", './/strong[text()="Far:"]/following-sibling::a[1]')
        sire_info.add_xpath(
            "country", './/strong[text()="Far:"]/following-sibling::a[1]'
        )

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(
            item=NorwegianRegistration(),
            selector=selector.xpath("./tr[2]"),
        )

        sire_registration.add_value("source", "DNT")

        sire_registration.add_xpath(
            "name", './/strong[text()="Far:"]/following-sibling::a[1]'
        )
        sire_registration.add_xpath(
            "link", './/strong[text()="Far:"]/following-sibling::a[1]/@href'
        )

        sire.add_value("registrations", sire_registration.load_item())

        horse.add_value("sire", sire.load_item())

        dam = ItemLoader(item=NorwegianHorse())

        dam_info = ItemLoader(
            item=NorwegianHorseInfo(),
            selector=selector.xpath("./tr[2]"),
        )

        dam_info.add_value("gender", "mare")

        dam_info.add_xpath("name", './/strong[text()="Mor:"]/following-sibling::a')
        dam_info.add_xpath("country", './/strong[text()="Mor:"]/following-sibling::a')

        dam.add_value("horse_info", dam_info.load_item())

        dam_registration = ItemLoader(
            item=NorwegianRegistration(),
            selector=selector.xpath("./tr[2]"),
        )

        dam_registration.add_value("source", "DNT")

        dam_registration.add_xpath(
            "name", './/strong[text()="Mor:"]/following-sibling::a'
        )
        dam_registration.add_xpath(
            "link", './/strong[text()="Mor:"]/following-sibling::a/@href'
        )

        dam.add_value("registrations", dam_registration.load_item())

        horse.add_value("dam", dam.load_item())

    starter.add_value("starter_info", starter_info.load_item())

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=NorwegianRegistration(),
        selector=selector.xpath('.//a[contains(@href,"horse")]'),
    )

    registration.add_value("source", "DNT")

    registration.add_xpath("name", ".")
    registration.add_xpath("link", "./@href")

    horse.add_value("registrations", registration.load_item())

    starter.add_value("horse", horse.load_item())

    return starter
