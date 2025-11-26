import json
import scrapy
from itemloaders import ItemLoader
from scrapy.http.response import Response
from horses.items.sweden import SwedishHorse, SwedishHorseInfo
from horses.parsers.sweden.horse.st import (
    parse_chip,
    parse_horse_info,
    parse_offspring,
    parse_pedigree,
    parse_result_summaries,
    parse_starts,
)


SWEDISH_DOMAINS = ["travsport.se", "atg.se"]

ST_BASE_URL = "https://api.travsport.se/webapi/horses"
ST_SEARCH_URL = f"{ST_BASE_URL}/search/organisation/TROT"
ST_HORSE_BASIC_INFO = f"{ST_BASE_URL}/basicinformation/organisation/TROT/sourceofdata/SPORT/horseid/"
ST_HORSE_PEDIGREE = f"{ST_BASE_URL}/pedigree/organisation/TROT/sourceofdata/SPORT/horseid/"
ST_HORSE_CHIP_INFO = f"{ST_BASE_URL}/pedigree/description/organisation/TROT/sourceofdata/SPORT/horseid/"
ST_HORSE_OFFSPRING = f"{ST_BASE_URL}/offspring/organisation/TROT/sourceofdata/SPORT/horseid/"
ST_HORSE_RESULT_SUMMARIES = f"{ST_BASE_URL}/statistics/organisation/TROT/sourceofdata/SPORT/horseid/"
ST_HORSE_STARTS = f"{ST_BASE_URL}/results/organisation/TROT/sourceofdata/SPORT/horseid/"


class SwedenHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = SWEDISH_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                scrapy.http.JsonRequest,
                {
                    "url": f"{ST_SEARCH_URL}?age=0&gender=BOTH&"
                    f"horseName={self.name}&trotBreed=ALL&autoSuffixWildcard=true"
                },
            ),
        ]

    def handle_response(self, response: Response) -> None:
        self.parse_search_result(response)

    def parse_search_result(self, response: Response) -> None:
        res = json.loads(response.body)

        for horse in res:
            self.horses.append(SwedenHorse(horse_id=horse["horseId"]))


class SwedenHorse:
    def __init__(self, horse_id: int) -> None:
        self.horse_info = ItemLoader(item=SwedishHorseInfo())
        self.horse_id = horse_id
        self.horse = ItemLoader(item=SwedishHorse())

        self.requests = [
            (
                scrapy.http.JsonRequest,
                {
                    "url": f"{ST_HORSE_BASIC_INFO}{self.horse_id}"
                },
            ),
            (
                scrapy.http.JsonRequest,
                {
                    "url": f"{ST_HORSE_PEDIGREE}{self.horse_id}?pedigreeTree=SMALL"
                },
            ),
            (
                scrapy.http.JsonRequest,
                {
                    "url": f"{ST_HORSE_CHIP_INFO}{self.horse_id}"
                },
            ),
        ]

    def handle_response(self, response: Response) -> None:
        if "/basicinformation/" in response.url:
            self.parse_horse_info(response)
        elif "pedigreeTree" in response.url:
            self.parse_pedigree(response)
        elif "/results/" in response.url:
            self.parse_starts(response)
        elif "/offspring/" in response.url:
            self.parse_offspring(response)
        elif "/statistics/" in response.url:
            self.parse_result_summaries(response)
        elif "/description/" in response.url:
            self.horse_info.add_value("chip", parse_chip(response))

    def return_horse(self) -> dict:
        return self.horse.load_item()

    def parse_horse_info(self, response: Response) -> None:
        horse = parse_horse_info(response)

        self.horse_info = horse["horse_info"]

        self.horse.add_value("registrations", horse["registration"].load_item())

        if horse["offspring"]:
            self.requests.append(
                (
                    scrapy.http.JsonRequest,
                    {
                        "url": f"{ST_HORSE_OFFSPRING}{self.horse_id}"
                    },
                ),
            )

        if horse["starts"]:
            self.requests.extend(
                [
                    (
                        scrapy.http.JsonRequest,
                        {
                            "url": f"{ST_HORSE_RESULT_SUMMARIES}{self.horse_id}"
                        },
                    ),
                    (
                        scrapy.http.JsonRequest,
                        {
                            "url": f"{ST_HORSE_STARTS}{self.horse_id}"
                        },
                    ),
                ]
            )

    def parse_pedigree(self, response: Response) -> None:
        sire, dam = parse_pedigree(response)

        if sire:
            self.horse.add_value("sire", sire.load_item())

        if dam:
            self.horse.add_value("dam", dam.load_item())

    def parse_starts(self, response: Response) -> None:
        starts = parse_starts(response)

        for start in starts:
            self.horse.add_value("starts", start.load_item())

    def parse_offspring(self, response: Response) -> None:
        offspring = parse_offspring(response, self.horse_info.get_output_value("gender"))

        for horse in offspring:
            self.horse.add_value("offspring", horse.load_item())

    def parse_result_summaries(self, response: Response) -> None:
        summaries = parse_result_summaries(response)

        for summary in summaries:
            self.horse.add_value("result_summaries", summary.load_item())
