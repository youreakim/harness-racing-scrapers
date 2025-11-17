from parsel import Selector
import scrapy
from horses.items.italy import (
    ItalianHorse,
    ItalianHorseInfo,
    ItalianRegistration,
    ItalianResultSummary,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response


def parse_unire_search_result(response: Response) -> list[str | None]:
    return [
        row.xpath("./td[1]/a/@href").get()
        for row in response.xpath("//table/tbody/tr[.//a]")[1:]
    ]


def add_parents(
    horse: ItemLoader | None,
    sire: ItemLoader | None,
    dam: ItemLoader | None
) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def process_unire_pedigree_cell(cell: Selector) -> ItemLoader | None:
    if not cell.xpath(".//a"):
        return None

    ancestor = ItemLoader(item=ItalianHorse())

    ancestor_info = ItemLoader(item=ItalianHorseInfo(), selector=cell)

    ancestor_info.add_xpath("name", ".//a")
    ancestor_info.add_value("gender", "mare" if cell.xpath("./@class") else "horse")

    ancestor.add_value("horse_info", ancestor_info.load_item())

    ancestor_registration = ItemLoader(item=ItalianRegistration(), selector=cell)

    ancestor_registration.add_value("source", "unire")

    ancestor_registration.add_xpath("name", ".//a")
    ancestor_registration.add_xpath("link", ".//a/@href")

    ancestor.add_value("registrations", ancestor_registration.load_item())

    return ancestor


def populate_unire_pedigree(horse: ItemLoader, ancestors: list[ItemLoader | None]) -> None:
    horse_parents = [
        (1, 3, 4),
        (2, 5, 6),
        (8, 10, 11),
        (9, 12, 13),
        (0, 1, 2),
        (7, 8, 9),
    ]

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(ancestors[horse_index], ancestors[sire_index], ancestors[dam_index])

    add_parents(horse, ancestors[0], ancestors[7])


def parse_horse_info(response: Response, horse: ItemLoader) -> None:
    horse_info = ItemLoader(
        item=ItalianHorseInfo(), selector=response.xpath("//div[@class='news-home']")
    )

    horse_info.add_xpath("name", "./p[1]")
    horse_info.add_xpath(
        "gender",
        "./table[1]//tr[td[contains(text(),'nato nel')]]/following-sibling::tr[1]/td[1]",
    )
    horse_info.add_xpath(
        "birthdate",
        "./table[1]//tr[td[contains(text(),'nato nel')]]/following-sibling::tr[1]/td[3]",
    )
    horse_info.add_xpath(
        "country",
        "./table[1]//tr[td[contains(text(),'nato nel')]]/following-sibling::tr[1]/td[4]",
    )
    horse_info.add_xpath(
        "chip",
        "./table[1]//tr[td[contains(text(),'microchip')]]/following-sibling::tr[1]/td[1]",
    )
    horse_info.add_xpath(
        "breeder",
        "./table[1]//tr[td[contains(text(),'microchip')]]/following-sibling::tr[1]/td[2]",
    )

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=ItalianRegistration(), selector=response.xpath("//div[@class='news-home']")
    )

    registration.add_value("source", "unire")
    registration.add_value("link", response.url)

    registration.add_xpath("name", "./p[1]")
    registration.add_xpath(
        "registration",
        "./table[1]//tr[td[contains(text(),'Tipologia Isrizione')]]/following-sibling::tr[1]/td[1]",
    )

    horse.add_value("registrations", registration.load_item())

    ancestors = [
        process_unire_pedigree_cell(cell)
        for cell in response.xpath(
            "//h5[text()='Genealogia']/following-sibling::table[1]//td[not(table)]"
        )
    ]

    populate_unire_pedigree(horse, ancestors)

    result_summary = ItemLoader(
        item=ItalianResultSummary(),
        selector=response.xpath("//tr[td/a[text()='carriera']]"),
    )

    result_summary.add_xpath("starts", "./td[2]")

    if result_summary.get_output_value("starts") != 0:
        result_summary.add_xpath("wins", "./td[3]")
        result_summary.add_xpath("mark", "./td[5]")
        result_summary.add_xpath("earnings", "./td[6]")

        horse.add_value("result_summaries", result_summary.load_item())


def parse_unire_horse_info(response: Response, horse: ItemLoader, requests: list, meta: dict) -> None:
    parse_horse_info(response, horse)

    if response.xpath("//input[@name='Discendenza']"):
        career_link = response.xpath("//a[text()='carriera']/@href").get()

        link_splits = career_link.split("/")

        url = f"https://www.unire.gov.it/index.php/ita/trotto/disc_cavallo/{'/'.join(link_splits[2:4])}/{link_splits[4][0].upper()}/1"

        requests.append(
            (
                scrapy.FormRequest,
                {
                    "url": url,
                    "formdata": {
                        f"{'m' if url[-1] == 'M' else ''}children": "1",
                        "Discendenza": "Discendenza",
                    },
                    "meta": meta,
                },
            )
        )


def parse_unire_offspring(response: Response, horse: ItemLoader, gender: str) -> None:
    for row in response.xpath("//tr[.//a]"):
        offspring = ItemLoader(item=ItalianHorse())

        offspring_info = ItemLoader(item=ItalianHorseInfo(), selector=row)

        offspring_info.add_xpath("name", "./td[1]/a")
        offspring_info.add_xpath("gender", "./td[2]")

        if gender == "horse":
            offspring_info.add_value("birthdate", response.url[-4:])
            offspring_info.add_xpath("country", "./td[4]")
        else:
            offspring_info.add_xpath("birthdate", "./td[4]")
            offspring_info.add_xpath("country", "./td[5]")

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=ItalianRegistration(), selector=row)

        offspring_registration.add_value("source", "unire")

        offspring_registration.add_xpath("name", "./td[1]/a")
        offspring_registration.add_xpath("link", "./td[1]/a/@href")

        offspring.add_value("registrations", offspring_registration.load_item())

        parent = ItemLoader(item=ItalianHorse())

        parent_info = ItemLoader(item=ItalianHorseInfo(), selector=row)

        parent_info.add_value("gender", gender)

        parent_column = 5 if gender == "horse" else 6

        parent_info.add_xpath("name", f"./td[{parent_column}]/a")

        parent.add_value("horse_info", parent_info.load_item())

        parent_registration = ItemLoader(item=ItalianRegistration(), selector=row)

        parent_registration.add_value("source", "unire")

        parent_registration.add_xpath("name", f"./td[{parent_column}]/a")
        parent_registration.add_xpath("link", f"./td[{parent_column}]/a/@href")

        parent.add_value("registrations", parent_registration.load_item())

        offspring.add_value("dam" if gender == "horse" else "sire", parent.load_item())

        horse.add_value("offspring", offspring.load_item())


def parse_unire_sire_links(response: Response, requests: list[tuple]) -> None:
    requests.extend(
        [
            (scrapy.Request, {"url": f"{response.url[:-1]}{url}"})
            for url in response.xpath("//td/a/@href").getall()
        ]
    )
