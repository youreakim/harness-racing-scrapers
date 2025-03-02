import json

import scrapy
from horses.items.germany import GermanHorse
from horses.parsers.germany.horse.hvt import (
    parse_five_generation_pedigree,
    parse_horse_info,
    parse_horse_offspring,
    parse_horse_starts,
    parse_search_response,
    parse_three_generation_pedigree,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

GERMAN_DOMAINS = ["hvtonline.de"]
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}


class GermanyHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = GERMAN_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": "https://www.hvtonline.de/traberdaten/",
                    "meta": {
                        **META_PLAYWRIGHT,
                        "playwright_page_methods": [
                            PageMethod(
                                "wait_for_selector", "//input[@id='trabersuche']"
                            ),
                            PageMethod("type", "//input[@id='trabersuche']", self.name),
                            PageMethod("wait_for_timeout", 1000),
                        ],
                    },
                },
            ),
        ]

    def handle_response(self, response: Response) -> None:
        self.horses.extend(
            GermanyHorse(horse_id=horse_id)
            for horse_id in parse_search_response(response, self.name)
        )


class GermanyHorse:
    def __init__(self, horse_id: str) -> None:
        self.horse = ItemLoader(item=GermanHorse())
        self.horse_id = horse_id
        self.offspring_lists = []

        self.requests = [
            (
                scrapy.FormRequest,
                {
                    "url": "https://www.hvtonline.de/ajax/trabersuchechange.php",
                    "formdata": {"horseid": self.horse_id, "tab": f"{page}"},
                    "meta": META_PLAYWRIGHT,
                },
            )
            for page in range(5)
        ]

    def handle_response(self, response: Response) -> None:
        if len(self.requests) == 4:
            parse_horse_info(response, self.horse)
        elif len(self.requests) == 3:
            parse_horse_starts(response, self.horse)
        elif len(self.requests) == 2:
            self.offspring_lists = parse_three_generation_pedigree(response)
        elif len(self.requests) == 1:
            parse_five_generation_pedigree(response, self.horse, self.offspring_lists)
        elif len(self.requests) == 0:
            parse_horse_offspring(response, self.horse)

    def return_horse(self) -> dict:
        return self.horse.load_item()
