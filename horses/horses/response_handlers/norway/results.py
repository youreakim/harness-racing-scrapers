import arrow
import scrapy
from scrapy.http.response import Response
from horses.parsers.norway.results.dnt import parse_calendar, parse_raceday
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
        PageMethod("wait_for_selector", '//div[@class="table-wrapper"]')
    ],
}


class NorwayCalendar:
    def __init__(self, start_date: arrow.arrow.Arrow, end_date: arrow.arrow.Arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.requests = []
        self.allowed_domains = NORWEGIAN_DOMAINS

        self.start_date = start_date
        self.end_date = end_date

        current_date = self.start_date

        while current_date.date() <= self.end_date.date():
            self.requests.append(
                (
                    scrapy.FormRequest,
                    {
                        "url": f"https://www.travsport.no/sportsbasen/lopskalender/",
                        "meta": META_CALENDAR,
                        "formdata": {
                            "year": current_date.format("YYYY"),
                            "month": current_date.format("M"),
                            "trackid": "0",
                        },
                    },
                )
            )

            current_date = current_date.shift(months=1)

    def handle_response(self, response: Response) -> None:
        self.parse_calendar(response)

    def parse_calendar(self, response: Response) -> None:
        racedays = parse_calendar(response, self.start_date, self.end_date)

        for raceday in racedays:
            requests = [(scrapy.Request, {"url": raceday["url"], "meta": META_RACEDAY})]

            self.racedays[raceday["key"]] = NorwayRaceday(raceday["raceday"], requests)


class NorwayRaceday:
    def __init__(self, raceday: ItemLoader, requests: list[tuple], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        self.parse_raceday(response)

    def return_raceday(self) -> None:
        return self.raceday.load_item()

    def parse_raceday(self, response: Response) -> None:
        parse_raceday(response, self.raceday)
