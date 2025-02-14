import scrapy
from horses.parsers.australia.entries.ahr import parse_raceday_calendar, parse_races
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

CALENDAR_LINK = "https://www.harness.org.au"

AUSTRALIAN_DOMAINS = ["harness.org.au"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod(
            "wait_for_selector",
            "//div[h4[text()='Racing']]//div[@id='meetings-widget']",
        ),
        PageMethod(
            "click",
            "//div[h4[text()='Racing']]//div[@id='meetings-widget']//a[text()='More Meetings']",
        ),
        PageMethod("wait_for_selector", "table.meetingList"),
    ],
}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "div.raceListLinks")],
}


class AustraliaCalendar:
    def __init__(self):
        self.racedays = {}
        self.allowed_domains = AUSTRALIAN_DOMAINS

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": CALENDAR_LINK,
                    "meta": META_CALENDAR,
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        handlers = parse_raceday_calendar(response)

        for handler in handlers:
            raceday_handler = AustraliaRaceday(
                raceday=handler["raceday"],
                race_type=handler["race_type"],
                requests=[
                    (scrapy.Request, {"url": handler["url"], "meta": META_RACEDAY})
                ],
            )

            self.racedays[handler["raceday_key"]] = raceday_handler


class AustraliaRaceday:
    def __init__(self, raceday: ItemLoader, race_type: str, requests: list[tuple]):
        self.raceday = raceday
        self.race_type = race_type
        self.requests = requests

    def return_raceday(self) -> dict:
        return self.raceday.load_item()

    def handle_response(self, response: Response) -> None:
        parse_races(response, self.raceday, self.race_type)
