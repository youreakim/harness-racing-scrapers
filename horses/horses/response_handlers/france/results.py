import arrow
import scrapy
from arrow.arrow import Arrow
from horses.parsers.france.results.letrot import parse_calendar, parse_race
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

FRENCH_DOMAINS = ["letrot.com"]
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//a[@id="race-card-2"]')
    ],
}
META_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//table[@id="originqualifications"]//a')
    ],
}


class FranceCalendar:
    def __init__(self, start_date: Arrow, end_date: Arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = FRENCH_DOMAINS
        self.requests = []

        for date in arrow.Arrow.range("day", start_date, end_date):
            self.requests.append(
                (
                    scrapy.Request,
                    {
                        "url": f"https://www.letrot.com/courses/{date.date().isoformat()}",
                        "meta": META_CALENDAR,
                    },
                )
            )

    def handle_response(self, response: Response) -> None:
        racedays = parse_calendar(response)

        for raceday in racedays:
            requests = [
                (
                    scrapy.Request,
                    {
                        "url": url,
                        "meta": META_RACE,
                    },
                )
                for url in raceday["urls"]
            ]

            self.racedays[raceday["key"]] = FranceRaceday(
                raceday=raceday["raceday"], requests=requests
            )


class FranceRaceday:
    def __init__(self, raceday: ItemLoader, requests: list[tuple], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        parse_race(response, self.raceday)

    def return_raceday(self) -> None:
        return self.raceday.load_item()
