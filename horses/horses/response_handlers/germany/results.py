import scrapy
from horses.parsers.germany.results.hvt import (
    parse_calendar,
    parse_race,
    parse_raceday_links,
)
from scrapy_playwright.page import PageMethod

GERMAN_DOMAINS = ["hvtonline.de"]
GERMAN_META = {
    "playwright": True,
    "playwright_include_page": True,
    "playwright_page_methods": [PageMethod("wait_for_selector", "div#cardhistory")],
}

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
        PageMethod("wait_for_selector", '//div[contains(@class,"raceheader")]')
    ],
}
META_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//div[@id="cardshort"]')
    ],
}


class GermanyCalendar:
    def __init__(self, start_date, end_date, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_date = start_date
        self.end_date = end_date
        self.racedays = {}
        self.requests = []
        self.allowed_domains = GERMAN_DOMAINS

        current_date = self.start_date

        while current_date <= self.end_date:
            self.requests.append(
                (
                    scrapy.Request,
                    {
                        "url": f'https://www.hvtonline.de/monatsrennberichte/{current_date.format("YYYYMM")}/',
                        "meta": META_CALENDAR,
                    },
                )
            )

            current_date = current_date.shift(months=1)

    def handle_response(self, response):
        racedays = parse_calendar(response)

        for raceday in racedays:
            if self.start_date.date() <= raceday["date"] <= self.end_date.date():
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
    def __init__(self, raceday, requests=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response):
        last_url_split = response.url.split("/")[-1]

        if len(last_url_split) == 8:
            self.requests.extend(
                (scrapy.Request, {"url": x, "meta": META_RACE})
                for x in parse_raceday_links(response)
            )
        else:
            parse_race(response, self.raceday)

    def return_raceday(self):
        return self.raceday.load_item()
