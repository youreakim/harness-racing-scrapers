import arrow
import scrapy
from horses.parsers.denmark.results.travinfo import parse_calendar, parse_races

DENMARK_DOMAINS = ["danskhv.dk"]


class DenmarkCalendar:
    def __init__(self, start_date, end_date, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.requests = []
        self.allowed_domains = DENMARK_DOMAINS

        self.start_date = start_date
        self.end_date = end_date

        current_date = self.start_date

        while current_date <= self.end_date:
            self.requests.append(
                (
                    scrapy.http.JsonRequest,
                    {
                        "url": f"https://api.danskhv.dk/webapi/trot/raceinfo/racedays"
                        f'?fromracedate={current_date.floor("month").date().isoformat()}'
                        f'&toracedate={current_date.ceil("month").date().isoformat()}'
                    },
                )
            )

            current_date = current_date.shift(months=1)

    def handle_response(self, response):
        racedays = parse_calendar(response)

        for raceday in racedays:
            raceday_date = arrow.get(
                raceday["raceday"].get_output_value("raceday_info")["date"],
                "YYYY-MM-DD",
            )

            if self.start_date.date() <= raceday_date.date() <= self.end_date.date():
                requests = [
                    (
                        scrapy.http.JsonRequest,
                        {"url": raceday["url"]},
                    )
                ]

                raceday_parser = DenmarkRaceday(
                    raceday=raceday["raceday"], requests=requests
                )

                key = raceday["key"]

                self.racedays[key] = raceday_parser


class DenmarkRaceday:
    def __init__(self, raceday, requests=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = [] if requests is None else requests

    def return_raceday(self):
        return self.raceday.load_item()

    def handle_response(self, response):
        parse_races(response, self.raceday)
