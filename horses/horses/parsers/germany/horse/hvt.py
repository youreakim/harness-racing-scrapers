from horses.items.germany import (
    GermanHorse,
    GermanHorseInfo,
    GermanRace,
    GermanRaceday,
    GermanRacedayInfo,
    GermanRaceInfo,
    GermanRaceStarter,
    GermanRaceStarterInfo,
    GermanRaceStarterOdds,
    GermanRaceStarterTime,
    GermanRegistration,
)
from itemloaders import ItemLoader
from parsel import Selector
from scrapy.http.response import Response


def handle_pedigree_cell(cell: Selector) -> ItemLoader | None:
    if "nodata" in cell.attrib["class"]:
        return None

    ancestor = ItemLoader(item=GermanHorse())

    ancestor_info = ItemLoader(item=GermanHorseInfo(), selector=cell)

    ancestor_info.add_value(
        "gender", "horse" if cell.attrib["class"].startswith("vater") else "mare"
    )

    ancestor_info.add_xpath("name", "./text()[1]")
    ancestor_info.add_xpath("country", "./text()[1]")

    ancestor.add_value("horse_info", ancestor_info.load_item())

    ancestor_registration = ItemLoader(item=GermanRegistration(), selector=cell)

    ancestor_registration.add_value("source", "hvt")

    ancestor_registration.add_xpath("name", "./text()[1]")
    ancestor_registration.add_xpath("link", "./@data-traberid")

    ancestor.add_value("registrations", ancestor_registration.load_item())

    return ancestor


def add_parents(
    horse: ItemLoader | None, sire: ItemLoader | None, dam: ItemLoader | None
) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def populate_pedigree(horse: ItemLoader, ancestors: list[ItemLoader | None]) -> None:
    horse_parents = []

    for offspring_offset, parent_offset, index_range in [
        (32, 0, 16),
        (48, 32, 8),
        (56, 48, 4),
        (60, 56, 2),
    ]:
        horse_parents.extend(
            [
                (offspring_offset + x, parent_offset + 2 * x, parent_offset + 1 + 2 * x)
                for x in range(index_range)
            ]
        )

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(ancestors[horse_index], ancestors[sire_index], ancestors[dam_index])

    add_parents(horse, ancestors[60], ancestors[61])


def parse_search_response(response: Response, name: str) -> list[str]:
    ids = []

    for row in response.xpath("//div[@class='autocomplete-suggestion']"):
        horse_id = row.xpath("./@data-horseid").get()
        horse_name = row.xpath("./@data-horsename").get()

        if horse_name and horse_name.strip().lower().startswith(name.strip().lower()):
            ids.append(horse_id)

    return ids


def parse_horse_info(response: Response, horse: ItemLoader) -> None:
    text = str(response.body, "UTF-8")
    text = text.replace("""/""", "/").replace("&gt;", ">").replace("&lt;", "<")

    sel = Selector(text=text[text.find(',"html":') + 8 : text.rfind("}")])

    horse_info = ItemLoader(item=GermanHorseInfo(), selector=sel)

    horse_info.add_xpath(
        "name", './/td[text()="Name des Trabers:"]/following-sibling::td'
    )
    horse_info.add_xpath(
        "country", './/td[text()="Name des Trabers:"]/following-sibling::td'
    )
    horse_info.add_xpath("gender", './/td[text()="Geschlecht:"]/following-sibling::td')
    horse_info.add_xpath(
        "birthdate", './/td[text()="Geburtsdatum:"]/following-sibling::td'
    )
    horse_info.add_xpath("ueln", './/span[@class="three"]')

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=GermanRegistration(), selector=sel)

    registration.add_value("source", "hvt")

    registration.add_xpath(
        "name", '//td[text()="Name des Trabers:"]/following-sibling::td'
    )
    registration.add_xpath("link", '//span[@class="two"]')

    horse.add_value("registrations", registration.load_item())


def parse_three_generation_pedigree(response: Response) -> list[list[ItemLoader]]:
    offspring_generations = []

    for generation_table in response.xpath('//table[@class="produkte"]'):
        offspring_list = []

        for row in generation_table.xpath("./tbody/tr[position()>1]"):
            offspring = ItemLoader(item=GermanHorse())

            offspring_info = ItemLoader(item=GermanHorseInfo(), selector=row)

            offspring_info.add_xpath("name", "./td[2]/a")
            offspring_info.add_xpath("birthdate", "./td[1]")

            offspring.add_value("horse_info", offspring_info.load_item())

            offspring_registration = ItemLoader(item=GermanRegistration(), selector=row)

            offspring_registration.add_value("source", "hvt")

            offspring_registration.add_xpath("name", "./td[2]/a")
            offspring_registration.add_xpath("link", "./td[2]/a/@data-traberid")

            offspring.add_value("registrations", offspring_registration.load_item())

            offspring_list.append(offspring.load_item())

        offspring_generations.append(offspring_list)

    return offspring_generations


def parse_five_generation_pedigree(
    response: Response, horse: ItemLoader, offspring_generations: list[list[ItemLoader]]
) -> None:
    ancestors = [
        handle_pedigree_cell(ancestor_cell)
        for ancestor_cell in response.xpath('//div[@class="generations" and a]/a')
    ]

    if len(offspring_generations[0]) != 0 and ancestors[61]:
        ancestors[61].add_value("offspring", offspring_generations[0])

    if len(offspring_generations[1]) != 0 and ancestors[59]:
        ancestors[59].add_value("offspring", offspring_generations[1])

    if len(offspring_generations[2]) != 0 and ancestors[55]:
        ancestors[55].add_value("offspring", offspring_generations[2])

    populate_pedigree(horse, ancestors)


def parse_horse_offspring(response: Response, horse: ItemLoader) -> None:
    for offspring_row in response.xpath(
        '//table[@class="gestuetbuch"]/tbody/tr[count(td)>1]'
    ):
        offspring = ItemLoader(item=GermanHorse())

        offspring_info = ItemLoader(item=GermanHorseInfo(), selector=offspring_row)

        offspring_info.add_xpath("name", ".//a")
        offspring_info.add_xpath("country", ".//a")
        offspring_info.add_xpath("birthdate", "./td[1]")
        offspring_info.add_xpath("gender", "./td[4]")

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(
            item=GermanRegistration(), selector=offspring_row
        )

        offspring_registration.add_value("source", "hvt")

        offspring_registration.add_xpath("name", ".//a")
        offspring_registration.add_xpath("link", ".//a/@data-traberid")

        offspring.add_value("registrations", offspring_registration.load_item())

        horse.add_value("offspring", offspring.load_item())


def parse_horse_starts(response: Response, horse: ItemLoader) -> None:
    for row in response.xpath(
        "//table[@class='leistungenmain']/tbody/tr[count(td)=11]"
    ):
        raceday = ItemLoader(item=GermanRaceday())

        raceday_info = ItemLoader(item=GermanRacedayInfo(), selector=row)

        raceday_info.add_value("status", "result")

        raceday_info.add_xpath("date", "./td[1]")
        raceday_info.add_xpath("racetrack", "./td[2]")

        raceday_info.add_xpath("country", "./td[2]")

        raceday.add_value("raceday_info", raceday_info.load_item())

        race = ItemLoader(item=GermanRace())

        race_info = ItemLoader(item=GermanRaceInfo(), selector=row)

        race_info.add_xpath("startmethod", "./td[7]")
        race_info.add_xpath("racetype", "./td[8]")

        race.add_value("race_info", race_info.load_item())

        starter = ItemLoader(item=GermanRaceStarter())

        starter_info = ItemLoader(item=GermanRaceStarterInfo(), selector=row)

        starter_info.add_xpath("finish", "./td[4]")
        starter_info.add_xpath("distance", "./td[6]")
        starter_info.add_xpath("startnumber", "./td[9]")
        starter_info.add_xpath("driver", "./following-sibling::tr[1]/td[2]")

        if race_info.get_output_value("racetype") == "race":
            starter_info.add_xpath("purse", "./td[11]")

            odds = ItemLoader(item=GermanRaceStarterOdds(), selector=row)

            odds.add_value("odds_type", "win")

            odds.add_xpath("odds", "./td[10]")

            starter.add_value("odds", odds.load_item())

        starter.add_value("starter_info", starter_info.load_item())

        if not row.xpath("./td[position()=5 and contains(text(),'o.Z.')]"):
            starter_time = ItemLoader(item=GermanRaceStarterTime(), selector=row)

            starter_time.add_value("from_distance", 0)
            starter_time.add_value(
                "to_distance", starter_info.get_output_value("distance")
            )
            starter_time.add_value("time_format", "km")

            starter_time.add_xpath("time", "./td[5]")

            starter.add_value("times", starter_time.load_item())

        race.add_value("race_starters", starter.load_item())

        raceday.add_value("races", race.load_item())

        horse.add_value("starts", raceday.load_item())
