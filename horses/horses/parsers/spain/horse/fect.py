import json

from parsel import Selector
from scrapy.http.response import Response
from horses.items.spain import (
    SpanishHorse,
    SpanishHorseInfo,
    SpanishRace,
    SpanishRaceday,
    SpanishRacedayInfo,
    SpanishRaceInfo,
    SpanishRaceLink,
    SpanishRaceStarter,
    SpanishRaceStarterInfo,
    SpanishRaceStarterTime,
    SpanishRegistration,
    SpanishResultSummary,
)
from itemloaders import ItemLoader
from w3lib.html import remove_tags


def parse_search_result(response: Response) -> list:
    horses = []

    res = json.loads(response.body)

    for horse_json in res["data"]:
        horse = ItemLoader(item=SpanishHorse())

        registration = ItemLoader(item=SpanishRegistration())

        registration.add_value("name", remove_tags(horse_json["nombre"]))
        registration.add_value("link", horse_json["id_caballo"])

        registration.add_value("source", "fect")

        horse.add_value("registrations", registration.load_item())

        horses.append({"horse": horse, "horse_id": horse_json["id_caballo"]})

    return horses


def add_parents(horse: ItemLoader | None, sire: ItemLoader | None, dam: ItemLoader | None) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def populate_pedigree(horse: ItemLoader, ancestors: list[ItemLoader | None]) -> None:
    horse_parents = []

    for generation in range(2, 0, -1):
        for ancestor in range(2**generation - 2, 2 ** (generation + 1) - 2):
            horse_parents.append((ancestor, (ancestor + 1) * 2, (ancestor + 1) * 2 + 1))

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(ancestors[horse_index], ancestors[sire_index], ancestors[dam_index])

    add_parents(horse, ancestors[horse_parents[-2][0]], ancestors[horse_parents[-1][0]])


def parse_result_summary(selector: Selector) -> ItemLoader:
    result_summary = ItemLoader(item=SpanishResultSummary(), selector=selector)

    result_summary.add_xpath("year", "./td[1]")
    result_summary.add_xpath("starts", "./td[13]")
    result_summary.add_xpath("wins", "./td[2]")
    result_summary.add_xpath("seconds", "./td[3]")
    result_summary.add_xpath("thirds", "./td[4]")
    result_summary.add_xpath("mark", "./td[14]")
    result_summary.add_xpath("earnings", "./td[15]")
        
    return result_summary


def parse_horse(response: Response, horse: ItemLoader) -> None:
    horse_info = ItemLoader(
        item=SpanishHorseInfo(),
        selector=response.xpath("//div[@id='kt_app_content_container']/div[1]")
    )

    horse_info.add_xpath("name", ".//div[text()='Nombre']//following-sibling::div")
    horse_info.add_xpath("ueln", ".//div[text()='UELN']//following-sibling::div")
    horse_info.add_xpath("birthdate", ".//div[text()='Año nacimiento']//following-sibling::div")
    horse_info.add_xpath("gender", ".//div[text()='Sexo']//following-sibling::div")
    horse_info.add_xpath("breeder", ".//div[text()='Criador']//following-sibling::div")

    horse.add_value("horse_info", horse_info.load_item())

    ancestors = parse_pedigree(response.xpath("//table[@class='recuadroRedondo']"))

    populate_pedigree(horse, ancestors)

    for row in response.xpath("//table[@id='tabla_anual']/tr"):
        result_summary = parse_result_summary(row)

        horse.add_value("result_summaries", result_summary.load_item())

    for start_row in response.xpath("//tr[contains(@id,'aCabTR_')]"):
        start = parse_start(start_row)

        horse.add_value("starts", start.load_item())


def parse_pedigree(selector: Selector) -> list[ItemLoader | None]:
    ancestors = []

    for count, cell in enumerate(selector.xpath(".//td[@class='recuadroTD']")):
        if not cell.xpath(".//a"):
            ancestors.append(None)
            continue

        ancestor = ItemLoader(item=SpanishHorse())

        ancestor_info = ItemLoader(item=SpanishHorseInfo(), selector=cell)

        ancestor_info.add_value("gender", "horse" if count % 2 == 0 else "mare")

        ancestor_info.add_xpath("name", ".//a")
        ancestor_info.add_xpath("country", ".//a")
        ancestor_info.add_xpath("birthdate", "./span/text()")

        ancestor.add_value("horse_info", ancestor_info.load_item())

        ancestor_registration = ItemLoader(
            item=SpanishRegistration(), selector=cell
        )

        ancestor_registration.add_value("source", "fect")

        ancestor_registration.add_xpath("name", ".//a")
        ancestor_registration.add_xpath("link", ".//a/@href")

        ancestor.add_value("registrations", ancestor_registration.load_item())

        ancestors.append(ancestor)

    return ancestors


def parse_start(selector: Selector) -> ItemLoader:
    raceday = ItemLoader(item=SpanishRaceday())

    raceday_info = ItemLoader(item=SpanishRacedayInfo(), selector=selector)

    raceday_info.add_xpath("date", "./td[1]")
    raceday_info.add_xpath("racetrack", "./td[position()=6 and string-length(text())>0]")

    raceday.add_value('raceday_info', raceday_info.load_item())

    race = ItemLoader(item=SpanishRace())

    race_info = ItemLoader(item=SpanishRaceInfo(), selector=selector)

    race_info.add_xpath("racename", "./td[2]")

    race_info.add_value("status", "results")

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=SpanishRaceLink(), selector=selector)

    race_link.add_xpath("link", "./td[2]/a/@href")

    race_link.add_value("source", "fect")

    race.add_value("links", race_link.load_item())

    starter = ItemLoader(item=SpanishRaceStarter())

    starter_info = ItemLoader(item=SpanishRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("driver", "./td[3]/a")
    starter_info.add_xpath("finish", "./td[5]")
    starter_info.add_xpath("disqualified", "./td[5]")
    starter_info.add_xpath("started", "./td[5]")
    starter_info.add_xpath("distance", "./td[7]")
    starter_info.add_xpath("purse", "./td[10]")

    starter.add_value("starter_info", starter_info.load_item())

    if selector.xpath("./td[position()=9 and string-length(text())>0]"):
        starter_time = ItemLoader(item=SpanishRaceStarterTime(), selector=selector)

        starter_time.add_xpath("time", "./td[9]")

        starter_time.add_value("from_distance", 0)
        starter_time.add_value("to_distance", starter_info.get_output_value("distance"))
        starter_time.add_value("time_format", "kilometer")

        starter.add_value("times", starter_time.load_item())

    race.add_value("race_starters", starter.load_item())

    raceday.add_value("races", race.load_item())

    return raceday
