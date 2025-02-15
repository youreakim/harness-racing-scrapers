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
    AustralianRaceStarterTime,
    AustralianRegistration,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy.selector.unified import Selector


def add_parents(
    horse: ItemLoader | None, sire: ItemLoader | None, dam: ItemLoader | None
) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def populate_pedigree(horse: ItemLoader, ancestors: list[ItemLoader | None]) -> None:
    horse_parents = [
        (2, 3, 4),
        (5, 6, 7),
        (9, 10, 11),
        (12, 13, 14),
        (17, 18, 19),
        (20, 21, 22),
        (24, 25, 26),
        (27, 28, 29),
        (1, 2, 5),
        (8, 9, 12),
        (16, 17, 20),
        (23, 24, 27),
        (0, 1, 8),
        (15, 16, 23),
    ]

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(ancestors[horse_index], ancestors[sire_index], ancestors[dam_index])

    add_parents(horse, ancestors[horse_parents[-2][0]], ancestors[horse_parents[-1][0]])


def parse_pedigree_cell(pedigree_cell: Selector) -> None | ItemLoader:
    if not pedigree_cell.xpath("./a"):
        return None

    ancestor = ItemLoader(item=AustralianHorse())

    ancestor_info = ItemLoader(item=AustralianHorseInfo(), selector=pedigree_cell)

    ancestor_info.add_value(
        "gender",
        (
            "horse"
            if pedigree_cell.xpath("./self::*[contains(@class,'sire')]")
            else "mare"
        ),
    )

    ancestor_info.add_xpath("name", "./a")
    ancestor_info.add_xpath("country", "./a")

    if pedigree_cell.xpath("./self::*[contains(@class,'penul')]"):
        pass
    else:
        ancestor_info.add_xpath("birthdate", 'substring-before(./a[2], "-")')

    ancestor.add_value("horse_info", ancestor_info.load_item())

    ancestor_registration = ItemLoader(
        item=AustralianRegistration(), selector=pedigree_cell
    )

    ancestor_registration.add_value("source", "ab")

    ancestor_registration.add_xpath("name", "./a")
    ancestor_registration.add_xpath("link", "./a/@href")

    ancestor.add_value("registrations", ancestor_registration.load_item())

    return ancestor


def parse_search_result(response: Response) -> list[dict]:
    horses = []

    for row in response.xpath("//table[.//tr[@class='RptHdrFont']]//tr[td[@class]]"):
        horse_id = row.xpath(".//a/@href").get()

        if horse_id:
            horse_id = horse_id[horse_id.rfind("/") + 1 :].strip()

            filly = row.xpath("./td[position()=2 and font[text()='Filly']]") is not None

            horses.append({"horse_id": horse_id, "filly": filly})

    return horses


def parse_horse_info(response: Response, horse: ItemLoader) -> None:
    horse_info = ItemLoader(
        item=AustralianHorseInfo(),
        selector=response.xpath('//table[@class="data"]'),
    )

    horse_info.add_xpath("name", './/td[@class="horseName"]')
    horse_info.add_xpath(
        "birthdate", './/td[text()="Foaling Date:"]/following-sibling::td[1]'
    )
    horse_info.add_xpath(
        "gender", './/td[text()="Colour/Sex:"]/following-sibling::td[1]'
    )
    horse_info.add_xpath(
        "country", './/td[text()="Country of birth:"]/following-sibling::td[1]'
    )
    horse_info.add_xpath(
        "chip", './/td[text()="Microchip(s):"]/following-sibling::td[1]'
    )
    horse_info.add_xpath("breeder", './/td[text()="Breeder:"]/following-sibling::td[1]')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=AustralianRegistration(), selector=horse_info.selector
    )

    registration.add_value("source", "ab")
    registration.add_value("link", response.url)

    registration.add_xpath("name", ".//td[@class='horseName']")

    horse.add_value("registrations", registration.load_item())


def parse_pedigree(response: Response, horse: ItemLoader) -> None:
    ancestor_cells = response.xpath('//table[@class="pedigree"]//td[@rowspan!="16"]')

    ancestors = [parse_pedigree_cell(cell) for cell in ancestor_cells]

    populate_pedigree(horse, ancestors)


def parse_offspring(response: Response, horse: ItemLoader) -> None:
    for row in response.xpath("//table[thead]/tbody/tr[td[position()=8 and .//a]]"):
        progeny = ItemLoader(item=AustralianHorse())

        progeny_info = ItemLoader(item=AustralianHorseInfo(), selector=row)

        progeny_info.add_xpath("birthdate", "./td[2]")
        progeny_info.add_xpath("gender", "./td[4]")
        progeny_info.add_xpath("name", "./td[8]/a")
        progeny_info.add_xpath("breeder", "./td[15]")

        progeny.add_value("horse_info", progeny_info.load_item())

        progeny_registration = ItemLoader(item=AustralianRegistration(), selector=row)

        progeny_registration.add_value("source", "ausbreed")

        progeny_registration.add_xpath("name", "./td[8]/a")
        progeny_registration.add_xpath("link", "./td[8]/a/@href")

        progeny.add_value("registrations", progeny_registration.load_item())

        sire = ItemLoader(item=AustralianHorse())

        sire_info = ItemLoader(
            item=AustralianHorseInfo(), selector=row.xpath("./td[9]/a")
        )

        sire_info.add_value("gender", "horse")

        sire_info.add_xpath("name", ".")

        sire.add_value("horse_info", sire_info.load_item())

        sire_registration = ItemLoader(
            item=AustralianRegistration(), selector=row.xpath("./td[9]/a")
        )

        sire_registration.add_value("source", "ausbreed")

        sire_registration.add_xpath("name", ".")
        sire_registration.add_xpath("link", "./@href")

        sire.add_value("registrations", sire_registration.load_item())

        progeny.add_value("sire", sire.load_item())

        horse.add_value("offspring", progeny.load_item())


def parse_starts(response: Response, horse: ItemLoader) -> None:
    for row in response.xpath("//table[2]//tr")[1:-1]:
        raceday = ItemLoader(item=AustralianRaceday())

        raceday_info = ItemLoader(item=AustralianRacedayInfo(), selector=row)

        raceday_info.add_xpath("date", "./td[1]")
        raceday_info.add_xpath("racetrack", "./td[2]")

        raceday.add_value("raceday_info", raceday_info.load_item())

        race = ItemLoader(item=AustralianRace())

        race_info = ItemLoader(item=AustralianRaceInfo(), selector=row)

        race_info.add_xpath("purse", "./td[6]")
        race_info.add_xpath("racename", "./td[7]")
        race_info.add_xpath("distance", "./td[9]")
        race_info.add_xpath("startmethod", "./td[11]")
        race_info.add_xpath("gait", "./td[13]")

        race.add_value("race_info", race_info.load_item())

        race_link = ItemLoader(item=AustralianRaceLink(), selector=row)

        race_link.add_value("source", "ausbreed")

        race_link.add_xpath("link", "./td[3]//a/@href")

        race.add_value("links", race_link.load_item())

        race_starter = ItemLoader(item=AustralianRaceStarter())

        starter_info = ItemLoader(item=AustralianRaceStarterInfo(), selector=row)

        starter_info.add_xpath("finish", "./td[4]")
        starter_info.add_xpath("purse", "./td[5]")
        starter_info.add_xpath("driver", "./td[8]")
        starter_info.add_xpath("distance", ["./td[9]", "./td[10]"])

        starter_time = ItemLoader(item=AustralianRaceStarterTime(), selector=row)

        starter_time.add_value("time_format", "mile")
        starter_time.add_value("from_distance", 0)
        starter_time.add_value("to_distance", starter_info.get_output_value("distance"))

        starter_time.add_xpath("time", "./td[15]")

        race_starter.add_value("times", starter_time.load_item())

        race_starter.add_value("starter_info", starter_info.load_item())

        race.add_value("race_starters", race_starter.load_item())

        raceday.add_value("races", race.load_item())

        horse.add_value("starts", raceday.load_item())
