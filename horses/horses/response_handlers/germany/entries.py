import scrapy
from horses.parsers.germany.entries.hvt import (
    parse_calendar,
    parse_race,
    parse_race_links,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

GERMAN_DOMAINS = ["hvtonline.de"]
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//div[@id="cardhistory"]')
    ],
}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//div[@class="rightcol"]')
    ],
}
META_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//div[@id="cardshort"]')
    ],
}


class GermanyCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = GERMAN_DOMAINS
        self.requests = [
            (
                scrapy.Request,
                {"url": "https://www.hvtonline.de/", "meta": META_CALENDAR},
            )
        ]

    def handle_response(self, response: Response) -> None:
        racedays = parse_calendar(response)

        for raceday in racedays:
            requests = [
                (
                    scrapy.Request,
                    {
                        "url": raceday["url"],
                        "meta": META_RACEDAY,
                    },
                )
            ]

            self.racedays[raceday["key"]] = GermanyRaceday(
                raceday=raceday["raceday"], requests=requests
            )


class GermanyRaceday:
    def __init__(
        self, raceday: ItemLoader, requests: list[tuple] | None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        last_url_split = response.url.split("/")[-1]

        if len(last_url_split) == 8:
            self.requests.extend(
                (scrapy.Request, {"url": x, "meta": META_RACE})
                for x in parse_race_links(response)
            )
        else:
            parse_race(response, self.raceday)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()
