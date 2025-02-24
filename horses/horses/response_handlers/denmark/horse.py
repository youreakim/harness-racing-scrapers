import json

from horses.items.denmark import DanishHorse, DanishHorseInfo
from horses.parsers.denmark.horse.travinfo import (
    parse_horse_chip,
    parse_horse_info,
    parse_offspring,
    parse_pedigree,
    parse_result_summary,
    parse_results,
)
from itemloaders import ItemLoader
from scrapy.http import JsonRequest

DENMARK_DOMAINS = ["danskhv.dk"]
BASE_URL = "https://api.danskhv.dk/webapi/trot"


class DenmarkHorseSearch:
    def __init__(self, name) -> None:
        self.allowed_domains = DENMARK_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                JsonRequest,
                {
                    "url": f"{BASE_URL}/horses/search?autoSuffixWildcard=false&autoPrefixWildcard=false&gender=BOTH&horseName={self.name}",
                },
            )
        ]

    def handle_response(self, response):
        if "search" in response.url:
            self.parse_search_result(response)

    def parse_search_result(self, response):
        res = json.loads(response.text)

        for horse in res:
            self.horses.append(DenmarkHorse(horse_id=horse["horseId"]))


class DenmarkHorse:
    def __init__(self, horse_id: int):
        self.horse = ItemLoader(item=DanishHorse())
        self.horse_info = ItemLoader(item=DanishHorseInfo())
        self.requests = [
            (
                JsonRequest,
                {"url": f"{BASE_URL}/horses/{horse_id}/basicinformation"},
            ),
            (
                JsonRequest,
                {"url": f"{BASE_URL}/horses/{horse_id}/pedigree/description"},
            ),
            (
                JsonRequest,
                {"url": f"{BASE_URL}/horses/{horse_id}/pedigree?pedigreeTree=SMALL"},
            ),
            (
                JsonRequest,
                {"url": f"{BASE_URL}/horses/{horse_id}/offspring"},
            ),
            (
                JsonRequest,
                {"url": f"{BASE_URL}/horses/{horse_id}/statistics"},
            ),
            (JsonRequest, {"url": f"{BASE_URL}/horses/{horse_id}/results"}),
        ]

    def handle_response(self, response):
        if "basicinformation" in response.url:
            parse_horse_info(response, self.horse, self.horse_info)
        elif "description" in response.url:
            parse_horse_chip(response, self.horse, self.horse_info)
        elif "pedigree" in response.url:
            parse_pedigree(response, self.horse)
        elif "offspring" in response.url:
            parse_offspring(response, self.horse)
        elif "statistics" in response.url:
            parse_result_summary(response, self.horse)
        elif "results" in response.url:
            parse_results(response, self.horse)

    def return_horse(self):
        return self.horse.load_item()
