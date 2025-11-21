import arrow
import scrapy
from horses.parsers.norway.entries.dnt import parse_calendar, parse_raceday
from itemloaders import ItemLoader
from scrapy_playwright.page import PageMethod

NORWEGIAN_DOMAINS = ["travsport.no"]
NORWEGIAN_META = {"playwright": True, "playwright_include_page": True}
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//a[text()="Proposisjoner"]')
    ],
}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//label[@for="expand-all"]'),
        PageMethod("click", selector='//label[@for="expand-all"]'),
    ],
}


class NorwayCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = NORWEGIAN_DOMAINS

        start_date = arrow.utcnow().shift(days=1)
        end_date = arrow.utcnow().shift(days=8)

        self.requests = [
            (
                scrapy.FormRequest,
                {
                    "url": "https://www.travsport.no/sportsbasen/lopskalender/",
                    "meta": META_CALENDAR,
                    "formdata": {
                        "year": start_date.format("YYYY"),
                        "month": start_date.format("M"),
                        "trackid": "0",
                    },
                },
            )
        ]

        if start_date.month != end_date.month:
            self.requests.append(
                (
                    scrapy.FormRequest,
                    {
                        "url": "https://www.travsport.no/sportsbasen/lopskalender/",
                        "meta": META_CALENDAR,
                        "formdata": {
                            "year": end_date.format("YYYY"),
                            "month": end_date.format("M"),
                            "trackid": "0",
                        },
                    },
                )
            )

    def handle_response(self, response):
        self.parse_calendar(response)

    def parse_calendar(self, response):
        racedays = parse_calendar(response)

        for raceday in racedays:
            requests = [(scrapy.Request, {"url": raceday["url"], "meta": META_RACEDAY})]

            self.racedays[raceday["key"]] = NorwayRaceday(raceday["raceday"], requests)


class NorwayRaceday:
    def __init__(self, raceday: ItemLoader, requests: list | None=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response):
        self.parse_raceday(response)

    def return_raceday(self):
        return self.raceday.load_item()

    def parse_raceday(self, response):
        parse_raceday(response, self.raceday)
