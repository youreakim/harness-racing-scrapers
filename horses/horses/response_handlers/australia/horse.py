import scrapy
from horses.items.australia import AustralianHorse
from horses.parsers.australia.horse.ausbreed import (
    parse_horse_info,
    parse_offspring,
    parse_pedigree,
    parse_search_result,
    parse_starts,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response

BASE_URL = "https://www.harness.org.au/ausbreed/reports"
AUSTRALIAN_DOMAINS = ["harness.org.au"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}


class AustraliaHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = AUSTRALIAN_DOMAINS
        self.name = name.replace(" ", "+")
        self.horses = []

        formdata = {
            "exact": "",
            "name1": self.name,
            "freezebrand": "",
            "microchip": "",
            "init": "",
            "B1": "Search",
        }

        self.requests = [
            (
                scrapy.FormRequest,
                {
                    "url": f"{BASE_URL}/search",
                    "formdata": formdata,
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        if "basic_results" in response.url:
            self.horses = [
                AustraliaHorse(**horse) for horse in parse_search_result(response)
            ]


class AustraliaHorse:
    def __init__(self, horse_id: str, filly: bool) -> None:
        self.requests = [
            (scrapy.Request, {"url": f"{BASE_URL}/performance/{horse_id}"}),
            (scrapy.Request, {"url": f"{BASE_URL}/pedigree/{horse_id}"}),
            (scrapy.Request, {"url": f"{BASE_URL}/start.cfm?horse_id={horse_id}"}),
        ]

        if filly:
            self.requests.append(
                (
                    scrapy.Request,
                    {"url": f"{BASE_URL}/m_progeny?horse_id={horse_id}"},
                )
            )

        self.horse = ItemLoader(item=AustralianHorse())

    def handle_response(self, response: Response) -> None:
        if "/performance/" in response.url:
            parse_horse_info(response, self.horse)

        elif "/pedigree/" in response.url:
            parse_pedigree(response, self.horse)

        elif "start.cfm" in response.url:
            parse_starts(response, self.horse)

        elif "m_progeny" in response.url:
            parse_offspring(response, self.horse)

    def return_horse(self) -> dict:
        return self.horse.load_item()
