import arrow
import scrapy
from horses.parsers.belgium.entries.trotting import parse_raceday_calendar, parse_races
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

RACEDAY_LINK = "https://www.trotting.be/races/"

BELGIAN_DOMAINS = ["trotting.be"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "div#no-more-tables")],
}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "div.card-body")],
}


class BelgiumCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.current_raceday = None
        self.allowed_domains = BELGIAN_DOMAINS

        start_date = arrow.utcnow().shift(days=1).date().isoformat()
        end_date = arrow.utcnow().shift(days=8).date().isoformat()

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"{RACEDAY_LINK}?hippodromeCode=NA&from={start_date}&to={end_date}",
                    "meta": META_CALENDAR,
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        handlers = parse_raceday_calendar(response)

        for handler in handlers:
            requests = [(scrapy.Request, {"url": handler["url"], "meta": META_RACEDAY})]

            raceday_handler = BelgiumRaceday(
                raceday=handler["raceday"], requests=requests
            )

            self.racedays[handler["raceday_key"]] = raceday_handler


class BelgiumRaceday:
    def __init__(self, raceday: ItemLoader, requests: list[tuple], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests

    def return_raceday(self):
        return self.raceday.load_item()

    def handle_response(self, response: Response) -> None:
        parse_races(response, self.raceday)
