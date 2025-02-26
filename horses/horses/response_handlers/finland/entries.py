import arrow
from horses.parsers.finland.entries.hippos import (
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = FINNISH_DOMAINS

        start_date = arrow.utcnow().shift(days=1).date().isoformat()
        end_date = arrow.utcnow().shift(days=7).date().isoformat()

        self.requests = [
            (
                JsonRequest,
                {"url": f"{BASE_URL}search/{start_date}/{end_date}/"},
            )
        ]

    def handle_response(self, response: Response) -> None:
        racedays = parse_raceday_calendar(response)

        for raceday in racedays:
            if raceday["key"] not in self.racedays:
                requests = [
                    (
                        JsonRequest,
                        {"url": raceday["url"]},
                    )
                ]

                raceday_parser = FinlandRaceday(
                    raceday=raceday["raceday"], requests=requests
                )

                self.racedays[raceday["key"]] = raceday_parser


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
                self.races[race["race_number"]] = race["race"]

                self.requests.append((JsonRequest, {"url": race["url"]}))

        else:
            parse_race(response, self.raceday, self.races)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()
