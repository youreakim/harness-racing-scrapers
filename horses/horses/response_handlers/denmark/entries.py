import arrow
from horses.parsers.denmark.entries.travinfo import parse_calendar, parse_races
from scrapy.http import JsonRequest

DENMARK_DOMAINS = ["danskhv.dk"]


class DenmarkCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.requests = []
        self.allowed_domains = DENMARK_DOMAINS

        self.start_date = arrow.now().shift(days=1)
        self.end_date = arrow.now().shift(days=5)

        current_date = self.start_date

        while current_date <= self.end_date:
            self.requests.append(
                (
                    JsonRequest,
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
                        JsonRequest,
                        {"url": raceday["url"]},
                    )
                ]

                raceday_parser = DenmarkRaceday(
                    raceday=raceday["raceday"], requests=requests
                )

                self.racedays[raceday["key"]] = raceday_parser


class DenmarkRaceday:
    def __init__(self, raceday, *args, requests=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = [] if requests is None else requests

    def return_raceday(self):
        return self.raceday.load_item()

    def handle_response(self, response):
        parse_races(response, self.raceday)
