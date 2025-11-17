import scrapy
from horses.items.italy import ItalianHorse
from horses.parsers.italy.horse.anact import (
    parse_anact_horse,
    parse_anact_search_result,
    parse_anact_starts,
)
from horses.parsers.italy.horse.unire import (
    parse_unire_horse_info,
    parse_unire_offspring,
    parse_unire_search_result,
    parse_unire_sire_links,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response

ITALIAN_DOMAINS = ["anact.it", "unire.gov.it"]
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}


class ItalyHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = ITALIAN_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"https://www.anact.it/autocomplete.php?object=cavalli&search={self.name}"
                },
            ),
            (
                scrapy.FormRequest,
                {
                    "url": "https://www.unire.gov.it/index.php/ita/trotto/list",
                    "formdata": {"name": self.name, "sex": "Tutti", "year": "Tutti"},
                    "meta": META_PLAYWRIGHT,
                },
            ),
        ]

    def handle_response(self, response: Response) -> None:
        if "unire" in response.url:
            self.horses.extend(
                ItalyHorse(horse_id=url[url.rfind("=") + 1 :], org="unire")
                for url in parse_unire_search_result(response)
            )
        elif "anact" in response.url:
            self.horses.extend(
                ItalyHorse(horse_id=horse_id, org="anact")
                for horse_id in parse_anact_search_result(response)
            )


class ItalyHorse:
    def __init__(self, horse_id: str, org: str) -> None:
        self.horse_id = horse_id
        self.horse = ItemLoader(item=ItalianHorse())

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": (
                        f"https://www.anact.it/genealogie/?codice={self.horse_id}"
                        if org == "anact"
                        else f"https://www.unire.gov.it/index.php/ita/trotto/list?id_cav={self.horse_id}"
                    ),
                    "meta": META_PLAYWRIGHT,
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        if "anact.it" in response.url:
            if "genealogie" in response.url:
                parse_anact_horse(response, self.horse, self.horse_id, self.requests)
            elif "scheda-cavallo" in response.url:
                parse_anact_starts(response, self.horse)
        elif "list?" in response.url:
            parse_unire_horse_info(response, self.horse, self.requests, META_PLAYWRIGHT)
        elif "/disc_cavallo/" in response.url:
            if "/F/" in response.url:
                parse_unire_offspring(response, self.horse, "mare")
            elif "/anno/" in response.url:
                parse_unire_offspring(response, self.horse, "horse")
            elif response.url.endswith("/M/1"):
                parse_unire_sire_links(response, self.requests)

    def return_horse(self) -> dict:
        return self.horse.load_item()
