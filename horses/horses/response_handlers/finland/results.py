from arrow.arrow import Arrow
from horses.parsers.finland.results.hippos import (
    parse_race,
    parse_raceday_calendar,
    parse_races,
)
from itemloaders import ItemLoader
from scrapy.http import JsonRequest
from scrapy.http.response import Response

BASE_URL = "https://heppa.hippos.fi/heppa2_backend/race/"

FINNISH_DOMAINS = ["hippos.fi"]


class FinlandCalendar:
    def __init__(self, start_date: Arrow, end_date: Arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = FINNISH_DOMAINS

        self.requests = [
            (
                JsonRequest,
                {
                    "url": f"{BASE_URL}search/{start_date.date().isoformat()}/{end_date.date().isoformat()}/"
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        racedays = parse_raceday_calendar(response)

        for raceday in racedays:
            requests = [
                (
                    JsonRequest,
                    {"url": raceday["url"]},
                )
            ]

            self.racedays[raceday["key"]] = FinlandRaceday(
                raceday=raceday["raceday"], requests=requests
            )


class FinlandRaceday:
    def __init__(self, raceday: ItemLoader, requests: list[tuple], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.races = {}
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        if response.url.endswith("/races"):
            races = parse_races(response, self.raceday)

            for race in races:
                self.requests.append((JsonRequest, {"url": race["url"]}))
                self.races[race["race_number"]] = race["race"]

        else:
            parse_race(response, self.raceday, self.races)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()
