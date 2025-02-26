import json

from horses.items.finland import FinnishHorse
from horses.parsers.finland.horse.hippos import (
    parse_horse_info,
    parse_offspring,
    parse_pedigree,
    parse_result_summary,
    parse_results,
)
from itemloaders import ItemLoader
from scrapy.http import JsonRequest
from scrapy.http.response import Response

BASE_URL = "https://heppa.hippos.fi/heppa2_backend"

FINNISH_DOMAINS = ["hippos.fi"]


class FinlandHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = FINNISH_DOMAINS
        self.name = name

        self.horses = []
        self.requests = [
            (
                JsonRequest,
                {"url": f"{BASE_URL}/search/all?term={self.name}&limit=5"},
            )
        ]

    def handle_response(self, response: Response) -> None:
        if "/search/" in response.url:
            self.parse_search_result(response)

    def parse_search_result(self, response: Response) -> None:
        res = json.loads(response.text)

        for horse in res["horses"]:
            self.horses.append(FinlandHorse(horse_id=horse["id"]))


class FinlandHorse:
    def __init__(self, horse_id: str) -> None:
        self.horse = ItemLoader(item=FinnishHorse())
        self.horse_id = horse_id

        self.requests = [
            (JsonRequest, {"url": f"{BASE_URL}/horse/{horse_id}"}),
            (JsonRequest, {"url": f"{BASE_URL}/horse/{horse_id}/stats"}),
            (
                JsonRequest,
                {
                    "url": f"{BASE_URL}/horse/{horse_id}/starts?pageNumber=1&pageSize=50&onlyResults=false"
                },
            ),
            (JsonRequest, {"url": f"{BASE_URL}/horse/{horse_id}/pedigree"}),
            (
                JsonRequest,
                {"url": f"{BASE_URL}/horse/{horse_id}/offsprings"},
            ),
        ]

    def handle_response(self, response: Response) -> None:
        if response.url.endswith(self.horse_id):
            parse_horse_info(response, self.horse)
        elif response.url.endswith("/stats"):
            parse_result_summary(response, self.horse)
        elif "/starts?" in response.url:
            add_request = parse_results(response, self.horse)

            if add_request:
                current_page = response.url[
                    response.url.find("&") - 2 : response.url.find("&")
                ]
                current_page = current_page.replace("=", "")

                self.requests.append(
                    (
                        JsonRequest,
                        {
                            "url": f"{BASE_URL}/horse/{self.horse_id}/starts?pageNumber={int(current_page) + 1}&pageSize=50&onlyResults=false"
                        },
                    )
                )
        elif response.url.endswith("/pedigree"):
            parse_pedigree(response, self.horse)
        elif response.url.endswith("/offsprings"):
            parse_offspring(response, self.horse)

    def return_horse(self) -> dict:
        return self.horse.load_item()
