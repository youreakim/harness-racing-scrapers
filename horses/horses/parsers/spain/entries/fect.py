import arrow
from parsel import Selector
from scrapy.http.response import Response
from horses.items.spain import (
    SpanishHorse,
    SpanishHorseInfo,
    SpanishRace,
    SpanishRaceday,
    SpanishRacedayInfo,
    SpanishRacedayLink,
    SpanishRaceInfo,
    SpanishRaceLink,
    SpanishRaceStarter,
    SpanishRaceStarterInfo,
    SpanishRegistration,
)
from itemloaders import ItemLoader


def parse_calendar(response: Response) -> list[dict]:
    racedays = []

    dates = [x.date().isoformat() for x in arrow.Arrow.range('days', arrow.utcnow().shift(days=1), arrow.utcnow().shift(days=5))]

    for date_node in response.xpath(
        '//td[@data-date and .//a[contains(@href,"jornada")]]'
    ):
        current_date = date_node.xpath("./@data-date").get()

        if current_date in dates:
            for link_node in date_node.xpath('.//a[contains(@href,"jornada")]'):
                raceday = ItemLoader(item=SpanishRaceday())

                raceday_info = ItemLoader(item=SpanishRacedayInfo(), selector=link_node)

                raceday_info.add_xpath("racetrack", ".")

                raceday_info.add_value("country", "spain")
                raceday_info.add_value("status", "entries")
                raceday_info.add_value("date", current_date)

                raceday.add_value("raceday_info", raceday_info.load_item())
                
                raceday_link = ItemLoader(item=SpanishRacedayLink(), selector=link_node)

                raceday_link.add_xpath("link", "./@href")

                raceday_link.add_value("source", "fect")

                raceday.add_value("links", raceday_link.load_item())

                key = f"{current_date}_{raceday_info.get_output_value('racetrack')}"
                url = f"https://federaciobaleardetrot.com/jornada.php?idPrograma={raceday_link.get_output_value('link')}"

                racedays.append({"raceday": raceday, "key": key, "url": url})

    return racedays


def parse_race_links(response: Response) -> list:
    links = []

    for link in response.xpath('//a/@href[contains(.,"verCarrera")]').getall():
        raceday_id = link[link.find("=") + 1 : link.rfind("&")]

        url = "https://www.federaciobaleardetrot.com/"
        pages = [
            ("mostrarCondicionesCarrera.php?idCarrera=", ""),
            ("verCarrera.php?idCarrera=", "&idTipo=1"),
            ("verCarrera.php?idCarrera=", "&idTipo=2"),
        ]

        for first, second in pages:
            links.append(f"{url}{first}{raceday_id}{second}")

    return links


def parse_race_info(response: Response) -> ItemLoader:
    race = ItemLoader(item=SpanishRace())

    race_info = ItemLoader(
        item=SpanishRaceInfo(), selector=response.xpath('//div[@class="well"]')
    )

    race_info.add_xpath(
        "racenumber", './/td[contains(text(),"Número")]/following-sibling::td'
    )
    race_info.add_xpath(
        "distance", './/td[contains(text(),"Distancia")]/following-sibling::td'
    )
    race_info.add_xpath(
        "startmethod", './/td[contains(text(),"Modo")]/following-sibling::td'
    )
    race_info.add_xpath("racename", "./h3/text()")
    race_info.add_xpath("conditions", "./div[2]/div/div")
    race_info.add_xpath("purse", 'substring-before(./div[2]/div/text(),"€")')

    race_info.add_value("status", "entries")
    race_info.add_value("gait", "trot")
    race_info.add_value("racetype", "race")

    race.add_value("race_info", race_info.load_item())

    race_link = ItemLoader(item=SpanishRaceLink())

    race_link.add_value("link", response.url)
    race_link.add_value("source", "fect")

    race.add_value("links", race_link.load_item())

    return race


def parse_race_starters_pedigrees(response: Response) -> list[dict]:
    pedigrees = []

    racenumber = response.xpath("substring-before(//b/text(),' - ')").get()

    if racenumber:

        racenumber = int(racenumber.strip())

        for pedigree_row in response.xpath('//table[@id="tabla_origenes"]//tr[td/a]'):
            link = pedigree_row.xpath("./td[2]/a/@href").get()

            link = link[link.rfind("=") + 1 :]

            sire, dam = parse_pedigree(pedigree_row)

            pedigrees.append({
                "racenumber": racenumber,
                "link": link,
                "sire": sire,
                "dam": dam
            })
    
    return pedigrees



def parse_pedigree(selector: Selector) -> tuple[ItemLoader, ItemLoader]:
    sire = ItemLoader(item=SpanishHorse())

    sire_info = ItemLoader(item=SpanishHorseInfo(), selector=selector)

    sire_info.add_value("gender", "horse")

    sire_info.add_xpath("name", "./td[3]/a")
    sire_info.add_xpath("country", "./td[3]/a")

    sire.add_value("horse_info", sire_info.load_item())

    sire_registration = ItemLoader(item=SpanishRegistration(), selector=selector)

    sire_registration.add_value("source", "fect")

    sire_registration.add_xpath("name", "./td[3]/a")
    sire_registration.add_xpath("link", "./td[3]/a/@href")

    sire.add_value("registrations", sire_registration.load_item())

    dam = ItemLoader(item=SpanishHorse())

    dam_info = ItemLoader(item=SpanishHorseInfo(), selector=selector)

    dam_info.add_value("gender", "mare")

    dam_info.add_xpath("name", "./td[4]/a")
    dam_info.add_xpath("country", "./td[4]/a")

    dam.add_value("horse_info", dam_info.load_item())

    dam_registration = ItemLoader(item=SpanishRegistration(), selector=selector)

    dam_registration.add_value("source", "fect")

    dam_registration.add_xpath("name", "./td[4]/a")
    dam_registration.add_xpath("link", "./td[4]/a/@href")

    dam.add_value("registrations", dam_registration.load_item())

    dam_sire = ItemLoader(item=SpanishHorse())

    dam_sire_info = ItemLoader(item=SpanishHorseInfo(), selector=selector)

    dam_sire_info.add_value("gender", "horse")

    dam_sire_info.add_xpath("name", "./td[5]/a")
    dam_sire_info.add_xpath("country", "./td[5]/a")

    dam_sire.add_value("horse_info", dam_sire_info.load_item())

    dam_sire_registration = ItemLoader(item=SpanishRegistration(), selector=selector)

    dam_sire_registration.add_value("source", "fect")

    dam_sire_registration.add_xpath("name", "./td[5]/a")
    dam_sire_registration.add_xpath("link", "./td[5]/a/@href")

    dam_sire.add_value("registrations", dam_sire_registration.load_item())

    dam.add_value("sire", dam_sire.load_item())

    return sire, dam


def parse_race_starters(response: Response) -> list[dict]:
    starters = []

    racenumber = response.xpath("substring-before(//b/text(),' - ')").get()

    if racenumber:
        racenumber = int(racenumber.strip())

        for starter_row in response.xpath(
            '//table[@id="tabla_participantes"]/tbody/tr'
        ):
            starter, horse = parse_starter(starter_row)

            starters.append({
                "racenumber": racenumber,
                "link": horse.get_output_value("registrations")[0]["link"],
                "starter": starter,
                "horse": horse
            })

    return starters

def parse_starter(selector: Selector) -> tuple[ItemLoader, ItemLoader]:
    starter = ItemLoader(item=SpanishRaceStarter())

    starter_info = ItemLoader(item=SpanishRaceStarterInfo(), selector=selector)

    starter_info.add_xpath("startnumber", "./td[1]")
    starter_info.add_xpath("driver", './/a[contains(@href,"datosConductor")]')
    starter_info.add_xpath("trainer", "./td[9]")
    starter_info.add_xpath("distance", "./td[11]")

    starter.add_value("starter_info", starter_info.load_item())

    horse = ItemLoader(item=SpanishHorse())

    horse_info = ItemLoader(item=SpanishHorseInfo(), selector=selector)

    horse_info.add_xpath("name", "./td[4]/a")
    horse_info.add_xpath("country", "./td[4]/a")
    horse_info.add_xpath("gender", "./td[7]")

    horse.add_value("horse_info", horse_info.load_item())

    registration = ItemLoader(item=SpanishRegistration(), selector=selector)

    registration.add_value("source", "fect")

    registration.add_xpath("name", "./td[4]/a")
    registration.add_xpath("link", "./td[4]/a/@href")

    horse.add_value("registrations", registration.load_item())

    return starter, horse
