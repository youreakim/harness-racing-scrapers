import scrapy
from arrow.arrow import Arrow
from horses.parsers.holland.results.ndr import parse_calendar, parse_raceday_info
from itemloaders import ItemLoader
from scrapy.http.response import Response

DUTCH_DOMAINS = ["ndr.nl"]


class HollandCalendar:
    def __init__(self, start_date: Arrow, end_date: Arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.start_date = start_date
        self.end_date = end_date
        self.allowed_domains = DUTCH_DOMAINS
        self.requests = []

        current_date = self.start_date

        while current_date.date() <= self.end_date.date():
            self.requests.append(
                (
                    scrapy.FormRequest,
                    {
                        "url": "https://ndr.nl/wp-admin/admin-ajax.php",
                        "formdata": {
                            "action": "zoek_koersen",
                            "archief": "true",
                            "jaar": f"{current_date.year}",
                            "maand": f"{current_date.month}",
                        },
                    },
                )
            )

            current_date = current_date.shift(months=1).floor("month")

    def handle_response(self, response: Response) -> None:
        racedays = parse_calendar(response)

        for raceday in racedays:
            if self.start_date.date() <= raceday["date"] <= self.end_date.date():
                requests = [
                    (
                        scrapy.FormRequest,
                        {
                            "url": "https://ndr.nl/wp-admin/admin-ajax.php",
                            "formdata": raceday["formdata"],
                        },
                    )
                ]

                self.racedays[raceday["key"]] = HollandRaceday(
                    raceday=raceday["raceday"], requests=requests
                )


class HollandRaceday:
    def __init__(
        self, raceday: ItemLoader, requests: list[tuple] | None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        parse_raceday_info(response, self.raceday)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()
