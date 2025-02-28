from horses.items.france import (
    FrenchHorse,
    FrenchHorseInfo,
    FrenchRegistration,
    FrenchResultSummary,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response


def add_parents(
    horse: ItemLoader | None, sire: ItemLoader | None, dam: ItemLoader | None
) -> None:
    if horse is not None:
        if sire is not None:
            horse.add_value("sire", sire.load_item())

        if dam is not None:
            horse.add_value("dam", dam.load_item())


def populate_tp_pedigree(
    horse: ItemLoader, ancestors: dict[str, ItemLoader | None]
) -> None:
    horse_parents = []

    for generation in range(4, 0, -1):
        for row in range(1, 2**generation + 1):
            horse_parents.append(
                (
                    f"{generation}_{row}",
                    f"{generation + 1}_{row * 2 - 1}",
                    f"{generation + 1}_{row * 2}",
                )
            )

    for horse_index, sire_index, dam_index in horse_parents:
        add_parents(
            ancestors.get(horse_index),
            ancestors.get(sire_index),
            ancestors.get(dam_index),
        )

    add_parents(horse, ancestors.get("1_1"), ancestors.get("1_2"))


def parse_search_tp(response: Response, name: str) -> list[str]:
    horse_ids = []

    for horse in response.xpath(
        f"//option[./text/nom[starts-with(text(),'{name.upper()}')]]"
    ):
        horse_id = horse.xpath("./@value").get()

        if horse_id:
            horse_ids.append(horse_id)

    return horse_ids


def parse_horse_tp(response: Response, horse: ItemLoader, horse_id: str) -> None:
    # self.family_id = response.xpath('//userdata[@name="numjb"]/text()').get()

    # self.requests.append((scrapy.Request, {'url': f'{TP_BASE_URL}/gridpjb.php?laj={self.family_id}&orderBy=6&direction=des'}))

    horse_info = ItemLoader(
        item=FrenchHorseInfo(), selector=response.xpath("//userdata[@name='lg1']")
    )

    horse_info.add_xpath("name", ".")
    horse_info.add_xpath("birthdate", ".")
    horse_info.add_xpath("country", ".")
    horse_info.add_xpath("gender", ".")

    horse.add_value("horse_info", horse_info.load_item())

    tp_registration = ItemLoader(
        item=FrenchRegistration(),
        selector=response.xpath("//userdata[@name='lg1']"),
    )

    tp_registration.add_value("source", "trot pedigree")
    tp_registration.add_value("link", horse_id)

    tp_registration.add_xpath("name", ".")

    horse.add_value("registrations", tp_registration.load_item())

    for link in response.xpath("//userdata[contains(text(),'https://')]"):
        registration = ItemLoader(item=FrenchRegistration(), selector=link)

        registration.add_xpath("source", "./@name")
        registration.add_xpath("link", ".")

        if registration.get_output_value("source"):
            horse.add_value("registrations", registration.load_item())

    ancestors = parse_pedigree_tp(response)

    populate_tp_pedigree(horse, ancestors)


def parse_offspring_tp(response: Response, horse: ItemLoader) -> None:
    year = 0

    for row in response.xpath("//item"):
        if row.xpath("./@id").get().strip().isnumeric():
            year = row.xpath("./@id").get().strip()
            continue

        offspring = ItemLoader(item=FrenchHorse())

        offspring_info = ItemLoader(item=FrenchHorseInfo(), selector=row)

        offspring_info.add_xpath("name", "./@text")

        offspring_info.add_value("birthdate", year)

        offspring.add_value("horse_info", offspring_info.load_item())

        offspring_registration = ItemLoader(item=FrenchRegistration(), selector=row)

        offspring_registration.add_value("source", "trot pedigree")

        offspring_registration.add_xpath("name", "./@text")
        offspring_registration.add_xpath("link", "./@id")

        offspring.add_value("registrations", offspring_registration.load_item())

        horse.add_value("offspring", offspring.load_item())


def parse_pedigree_tp(response: Response) -> dict[str, ItemLoader]:
    ancestors = {}

    for row in response.xpath("//userdata[contains(@name,'nom_')]"):
        key = row.xpath("substring(./@name,5)").get().strip()

        ancestor = ItemLoader(item=FrenchHorse())

        ancestor_info = ItemLoader(item=FrenchHorseInfo(), selector=row)

        ancestor_info.add_value("gender", ["mare", "horse"][int(key[-1]) % 2])

        ancestor_info.add_xpath("name", ".")

        ancestor.add_value("horse_info", ancestor_info.load_item())

        ancestor_registration = ItemLoader(item=FrenchRegistration(), selector=row)

        ancestor_registration.add_value("source", "trot pedigree")

        ancestor_registration.add_xpath("name", ".")
        ancestor_registration.add_value(
            "link", response.xpath(f'//userdata[@name="num_{key}"]').get()
        )

        ancestor.add_value("registrations", ancestor_registration.load_item())

        ancestors[key] = ancestor

    return ancestors
