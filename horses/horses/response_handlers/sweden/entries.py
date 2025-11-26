import arrow
from itemloaders import ItemLoader
import scrapy
from scrapy.http.response import Response
from horses.parsers.sweden.entries.st import parse_calendar, parse_races

SWEDISH_DOMAINS = ["travsport.se", "atg.se"]
BASE_URL = "https://api.travsport.se/webapi/raceinfo"
CALENDAR_URL = "/organisation/TROT/sourceofdata/SPORT"
RACEDAY_URL = "/startlists/organisation/TROT/sourceofdata/SPORT/racedayid/"



class SwedenCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = SWEDISH_DOMAINS

        start_date = arrow.utcnow().shift(days=1).date().isoformat()
        end_date = arrow.utcnow().shift(days=7).date().isoformat()

        self.requests = [
            (
                scrapy.http.JsonRequest,
                {
                    "url": f"{BASE_URL}{CALENDAR_URL}?fromracedate={start_date}"
                        f"&tosubmissiondate={end_date}&toracedate={end_date}"
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        self.parse_calendar(response)

    def parse_calendar(self, response: Response) -> None:
        racedays = parse_calendar(response)

        for raceday in racedays:
            requests = [
                (
                    scrapy.http.JsonRequest,
                    {
                        "url": f"{BASE_URL}{RACEDAY_URL}{raceday['raceday_id']}"
                    },
                )
            ]
            self.racedays[raceday["key"]] = SwedenRaceday(raceday=raceday["raceday"], requests=requests)


class SwedenRaceday:
    def __init__(self, raceday: ItemLoader, requests: list|None=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        self.parse_races(response)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()

    def parse_races(self, response: Response) -> None:
        parse_races(response, self.raceday)
