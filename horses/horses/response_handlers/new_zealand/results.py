import arrow
import scrapy
from scrapy.http.response import Response
from horses.parsers.new_zealand.results.hrnz import (
    parse_calendar,
    parse_race
)
from itemloaders import ItemLoader
from scrapy_playwright.page import PageMethod


NZ_DOMAINS = ["hrnz.co.nz"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "//th[contains(text(),'Search Results')]")
    ],
}
META_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "//table//tr//a")],
}


class NZCalendar:
    def __init__(self, start_date: str, end_date: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.start_date = arrow.get(start_date)
        self.end_date = arrow.get(end_date)
        self.allowed_domains = NZ_DOMAINS
        self.args = "&Arg=".join(
            [
                "hrnzg-Ptype",
                "RaceResults",
                "hrnzg-rSite",
                "TRUE",
                "hrnzg-ResultsType",
                "RacedaySearch",
                "hrnzg-ResultsYear",
                f'{self.start_date.format("YYYY")}',
                "hrnzg-ResultsMonth",
                f'{self.start_date.format("M")}',
                "hrnzg-ResultsDay",
                f'{self.start_date.format("D")}',
                "hrnzg-ResultsRacedayType",
                "OfficialRaces",
                "hrnzg-ResultsClubNo",
                "",
            ]
        )

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"https://harness.hrnz.co.nz/gws/ws/r/infohorsews/wsd06x?Arg={self.args}",
                    "meta": META_CALENDAR,
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        self.parse_calendar(response)

    def parse_calendar(self, response: Response) -> None:
        for raceday in parse_calendar(response):
            raceday_date = raceday.pop("raceday_date")

            if self.start_date.date() <= raceday_date <= self.end_date.date():
                key = (f'{raceday_date.isoformat()}_'
                        f'{raceday["raceday"].get_output_value("raceday_info")["racetrack"]}')

                self.racedays[key] = NZRacedayHandler(**raceday)

            if raceday_date > self.end_date.date():
                break
        else:
            if response.xpath('//input[@value="Next"]'):
                page_number = response.xpath(
                    '//input[@value="Next"]/preceding-sibling::input[last()]/@value'
                ).get()

                self.requests.append(
                    (
                        scrapy.Request,
                        {
                            "url": f"https://harness.hrnz.co.nz/gws/ws/r/infohorsews/"
                            f"wsd06x?Arg={self.args}&Arg=hrnzg-PageNumber&Arg={page_number}",
                            "meta": META_CALENDAR,
                        },
                    )
                )


class NZRacedayHandler:
    def __init__(self, raceday: ItemLoader, requests: list | None=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        if "RacesDisplay" in response.url:
            self.parse_raceday(response)
        elif "RaceDisplay" in response.url:
            self.parse_race(response)

    def return_raceday(self) -> dict:
        return self.raceday.load_item()

    def parse_raceday(self, response: Response) -> None:
        self.requests.extend(
            [
                (
                    scrapy.Request,
                    {"url": f"https://harness.hrnz.co.nz{link}", "meta": META_RACE},
                )
                for link in response.xpath("//table//td[1]/a/@href").getall()[:2]
            ]
        )

    def parse_race(self, response: Response) -> None:
        race = parse_race(response)

        self.raceday.add_value("races", race.load_item())
