import arrow
import scrapy
from horses.parsers.holland.entries.ndr import parse_calendar, parse_raceday_info
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

DUTCH_DOMAINS = ["ndr.nl"]
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "div.ndr-koers-titelbalk")
    ],
}
DUTCH_META = {
    "playwright": True,
    "playwright_include_page": True,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "div#ndr-search-results")
    ],
}


class HollandCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = DUTCH_DOMAINS
        self.requests = [
            (
                scrapy.FormRequest,
                {"url": "https://ndr.nl/selectieproeven/"},
            )
        ]

    def handle_response(self, response: Response) -> None:
        racedays = parse_calendar(response)

        for raceday in racedays:
            if arrow.get(raceday["date"]).date() > arrow.now().shift(days=3).date():
                continue

            requests = [
                (
                    scrapy.FormRequest,
                    {
                        "url": "https://ndr.nl/wp-admin/admin-ajax.php",
                        "meta": META_RACEDAY,
                        "formdata": raceday["formdata"],
                    },
                )
            ]

            self.racedays[raceday["key"]] = HollandRaceday(
                raceday=raceday["raceday"], requests=requests
            )


class HollandRaceday:
    def __init__(self, raceday: ItemLoader, requests: list[tuple], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        parse_raceday_info(response, self.raceday)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()
