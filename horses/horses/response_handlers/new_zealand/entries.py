from itemloaders import ItemLoader
import scrapy
from scrapy.http.response import Response
from horses.parsers.new_zealand.entries.hrnz import (
    parse_race,
    parse_raceday,
)
from scrapy_playwright.page import PageMethod

NZ_DOMAINS = ["hrnz.co.nz"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "//table//tr//a")
    ],
}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "div.accordion"),
        PageMethod("click", "button.hrnz-button--expand-all"),
        PageMethod("wait_for_selector", "tr.hrnz-participant"),
    ],
}


class NZCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.allowed_domains = NZ_DOMAINS
        self.requests = [
            (
                scrapy.Request,
                {
                    "url": "https://infohorse.hrnz.co.nz/datahrs/fields/fields.htm",
                    "meta": META_CALENDAR,
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        self.parse_calendar(response)

    def parse_calendar(self, response: Response) -> None:
        for row in response.xpath("//table//tr[td]"):
            raceday = parse_raceday(row)

            key = f"{raceday.get_output_value('raceday_info')['date']}_{raceday.get_output_value('raceday_info')['racetrack']}"

            requests = [
                (
                    scrapy.Request,
                    {
                        "url": f"{raceday.get_output_value('links')[0]['link']}",
                        "meta": META_RACEDAY,
                    },
                )
            ]

            self.racedays[key] = NZRaceday(raceday=raceday, requests=requests)


class NZRaceday:
    def __init__(self, raceday: ItemLoader, requests: list | None=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        self.parse_raceday(response)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()

    def parse_raceday(self, response: Response) -> None:
        for race_section in response.xpath('//div[contains(@id,"-race-") and a]'):
            race = parse_race(race_section)

            self.raceday.add_value("races", race.load_item())
