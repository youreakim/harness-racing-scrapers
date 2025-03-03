import scrapy
from horses.items.holland import DutchHorse
from horses.parsers.holland.horse.ndr import parse_horse, parse_search_result
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

DUTCH_DOMAINS = ["ndr.nl"]
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}


class HollandHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = DUTCH_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": "https://ndr.nl",
                    "meta": {
                        **META_PLAYWRIGHT,
                        "playwright_page_methods": [
                            PageMethod(
                                "wait_for_selector", "//form[@id='ndr-search-form']"
                            ),
                            PageMethod(
                                "type", "//input[@name='ndr-zoekterm']", self.name
                            ),
                            PageMethod("click", "//a[@id='ndr-search-submit']"),
                            PageMethod(
                                "wait_for_selector",
                                "//h2//div[@id='ndr-search-results']//li",
                            ),
                        ],
                    },
                },
            ),
        ]

    def handle_response(self, response: Response) -> None:
        self.horses.extend(
            HollandHorse(horse_id=horse_id)
            for horse_id in parse_search_result(response, self.name)
        )


class HollandHorse:
    def __init__(self, horse_id: str) -> None:
        self.horse = ItemLoader(item=DutchHorse())
        self.horse_id = horse_id

        self.requests = [
            (
                scrapy.FormRequest,
                {
                    "url": "https://ndr.nl/wp-admin/admin-ajax.php",
                    "formdata": {
                        "action": "do_search",
                        "categorie": "paard",
                        "type": "draf",
                        "id": self.horse_id,
                    },
                },
            ),
        ]

    def handle_response(self, response: Response) -> None:
        parse_horse(response, self.horse_id, self.horse)

    def return_horse(self) -> None:
        return self.horse.load_item()
