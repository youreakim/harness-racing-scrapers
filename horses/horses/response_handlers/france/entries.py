import arrow
import scrapy
from horses.parsers.france.entries.letrot import parse_calendar, parse_race
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
    "playwright_page_methods": [PageMethod("wait_for_selector", "table#raceleaving")],
}


class FranceCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = FRENCH_DOMAINS
        self.requests = []

        for offset in range(1, 2):
            self.requests.append(
                (
                    scrapy.Request,
                    {
                        "url": f"https://www.letrot.com/courses/"
                        f"{arrow.utcnow().shift(days=offset).date().isoformat()}",
                        "meta": META_PLAYWRIGHT,
                    },
                )
            )

    def handle_response(self, response: Response) -> None:
        racedays = parse_calendar(response)

        for raceday in racedays:
            requests = [
                (
                    scrapy.Request,
                    {"url": f"https://www.letrot.com{x}", "meta": META_RACE},
                )
                for x in raceday["urls"]
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
