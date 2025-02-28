import json
from math import ceil

from horses.items.france import FrenchHorse, FrenchHorseInfo, FrenchRegistration
from itemloaders import ItemLoader
from scrapy import Selector
from scrapy.http.response import Response


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

    for generation in range(4, 0, -1):
        for ancestor in range(2**generation - 2, 2 ** (generation + 1) - 2):
            horse_parents.append((ancestor, (ancestor + 1) * 2, (ancestor + 1) * 2 + 1))

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(ancestors[horse_index], ancestors[sire_index], ancestors[dam_index])

    add_parents(horse, ancestors[0], ancestors[1])


def parse_search_ifce(response: Response, name: str) -> list[str]:
    links = []

    res = json.loads(response.body)

    sel = Selector(text=res["resultats"])

    for article in sel.xpath("//article"):
        link = article.xpath(f".//a[text()='{name.upper()}']/@href").get()

        if link:
            links.append(link.split("/")[2])

    return links


def get_number_offspring_pages(response: Response) -> int:
    production = response.xpath(
        "//h4[text()='PRODUCTION']/following-sibling::p/text()"
    ).get()

    pages = 0

    if production:
        production = production.strip()

        if "sur" in production:
            production = production[production.find(" sur ") + 5 :].strip()

        number_offspring = int(production.split(" ")[0])

        pages = ceil(number_offspring / 100)

    return pages


def parse_horse_info_ifce(response: Response, horse: ItemLoader, horse_id: str) -> None:
    horse_info = ItemLoader(
        item=FrenchHorseInfo(),
        selector=response.xpath(
            "//h4[contains(text(),'stud-book')]/following-sibling::div[@class='card-body']"
        ),
    )

    horse_info.add_xpath(
        "ueln", ".//span[preceding-sibling::text()[contains(.,'Numéro UELN :')]]"
    )
    horse_info.add_xpath(
        "birthdate",
        ".//span[preceding-sibling::text()[contains(.,'Date de naissance :')]]",
    )
    horse_info.add_xpath(
        "country",
        ".//span[preceding-sibling::text()[contains(.,'Pays de naissance :')]]",
    )

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(
        item=FrenchRegistration(),
        selector=response.xpath(
            "//h4[contains(text(),'stud-book')]/following-sibling::div[@class='card-body']"
        ),
    )

    registration.add_value("source", "ifce")
    registration.add_value("link", horse_id)

    registration.add_xpath(
        "registration",
        ".//span[preceding-sibling::text()[contains(.,'Numéro SIRE :')]]",
    )

    horse.add_value("registrations", registration.load_item())


def parse_pedigree_ifce(response: Response, horse: ItemLoader) -> None:
    ancestors = []

    for generation in range(1, 6):
        for ancestor_cell in response.xpath(
            f"//div[@id='pedigree5G']/div[contains(@class,'box-gen{generation}')]"
            f"/div[@class='cheval']"
        ):
            if not ancestor_cell.xpath(".//a[@href]").get():
                ancestors.append(None)
                continue

            ancestor = ItemLoader(item=FrenchHorse())

            ancestor_info = ItemLoader(item=FrenchHorseInfo(), selector=ancestor_cell)

            ancestor_info.add_value(
                "gender", "horse" if len(ancestors) % 2 == 0 else "mare"
            )

            ancestor_info.add_xpath("name", "./span/a")
            ancestor_info.add_xpath("country", "./span/a")
            ancestor_info.add_xpath("ueln", "substring-after(./span/p,'UELN :')")

            ancestor.add_value("horse_info", ancestor_info.load_item())

            ancestor_registration = ItemLoader(
                item=FrenchRegistration(), selector=ancestor_cell
            )

            ancestor_registration.add_value("source", "ifce")

            ancestor_registration.add_xpath("name", "./span/a")
            ancestor_registration.add_xpath("link", "./span/a/@href")

            ancestor.add_value("registrations", ancestor_registration.load_item())

            ancestors.append(ancestor)

    populate_pedigree(horse, ancestors)


def parse_offspring_ifce(response: Response, horse: ItemLoader, horse_id: str) -> None:
    res = json.loads(response.body)

    sel = Selector(text=res["resultats"])

    for row in sel.xpath("//article"):
        offspring = ItemLoader(item=FrenchHorse())

        offspring_info = ItemLoader(item=FrenchHorseInfo(), selector=row)

        offspring_info.add_xpath("name", "./p[@class='mbn']/a")
        offspring_info.add_xpath(
            "country",
            row.xpath("./p[@class='mbn' and contains(text(),', Trotteur ')]"),
        )
        offspring_info.add_xpath(
            "gender", "./p[@class='mbn' and contains(text(),',')]/text()"
        )
        offspring_info.add_xpath(
            "birthdate", "./p[@class='mbn' and contains(text(),',')]/text()"
        )

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=FrenchRegistration(), selector=row)

        offspring_registration.add_value("source", "ifce")

        offspring_registration.add_xpath("name", "./p[@class='mbn']/a")
        offspring_registration.add_xpath("link", "./p[@class='mbn']/a/@href")

        offspring.add_value("registrations", offspring_registration.load_item())

        if row.xpath(
            f"./p[@class='mtn mbn']/a[position()=1 and contains(@href,'{horse_id}')]"
        ):
            # current horse is a horse, we need to find both dam and damsire
            dam = ItemLoader(item=FrenchHorse())

            dam_info = ItemLoader(
                item=FrenchHorseInfo(),
                selector=row.xpath("./p[@class='mtn mbn']/a[position()=2]"),
            )

            dam_info.add_value("gender", "mare")

            dam_info.add_xpath("name", ".")
            dam_info.add_xpath("country", "./following-sibling::text()[1]|.")

            dam.add_value("horse_info", dam_info.load_item())

            dam_registration = ItemLoader(
                item=FrenchRegistration(),
                selector=row.xpath("./p[@class='mtn mbn']/a[position()=2]"),
            )

            dam_registration.add_value("source", "ifce")

            dam_registration.add_xpath("name", ".")
            dam_registration.add_xpath("link", "./@href")

            dam.add_value("registrations", dam_registration.load_item())

            dam_sire = ItemLoader(item=FrenchHorse())

            dam_sire_info = ItemLoader(
                item=FrenchHorseInfo(),
                selector=row.xpath("./p[@class='mtn mbn']/a[position()=3]"),
            )

            dam_sire_info.add_value("gender", "horse")

            dam_sire_info.add_xpath("name", ".")
            dam_sire_info.add_xpath("country", "./following-sibling::text()[1]|.")

            dam_sire.add_value("horse_info", dam_sire_info.load_item())

            dam_sire_registration = ItemLoader(
                item=FrenchRegistration(),
                selector=row.xpath("./p[@class='mtn mbn']/a[position()=3]"),
            )

            dam_sire_registration.add_value("source", "ifce")

            dam_sire_registration.add_xpath("name", ".")
            dam_sire_registration.add_xpath("link", "./@href")

            dam_sire.add_value("registrations", dam_sire_registration.load_item())

            dam.add_value("sire", dam_sire.load_item())

            offspring.add_value("dam", dam.load_item())
        else:
            sire = ItemLoader(item=FrenchHorse())

            sire_info = ItemLoader(
                item=FrenchHorseInfo(),
                selector=row.xpath("./p[@class='mtn mbn']/a[position()=1]"),
            )

            sire_info.add_value("gender", "horse")

            sire_info.add_xpath("name", ".")
            sire_info.add_xpath("country", "./following-sibling::text()[1]|.")

            sire.add_value("horse_info", sire_info.load_item())

            sire_registration = ItemLoader(
                item=FrenchRegistration(),
                selector=row.xpath("./p[@class='mtn mbn']/a[position()=1]"),
            )

            sire_registration.add_value("source", "ifce")

            sire_registration.add_xpath("name", ".")
            sire_registration.add_xpath("link", "./@href")

            sire.add_value("registrations", sire_registration.load_item())

            offspring.add_value("sire", sire.load_item())

        horse.add_value("offspring", offspring.load_item())
