import scrapy
from arrow.arrow import Arrow
from horses.parsers.australia.results.ahr import parse_raceday_calendar, parse_races
from horses.parsers.australia.results.ausbreed import parse_ausbreed_race_result
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

BASE_URL = "https://www.harness.org.au/racing/results/"

AUSTRALIAN_DOMAINS = ["harness.org.au"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//table[@class="meetingListFull"]')
    ],
}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//div[@class="raceListLinks"]')
    ],
}
META_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//td[2]//a[contains(@href,"performance")]')
    ],
}


class AustraliaCalendar:
    def __init__(self, start_date: Arrow, end_date: Arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.start_date = start_date
        self.end_date = end_date
        self.allowed_domains = AUSTRALIAN_DOMAINS

        current_date = start_date

        self.requests = []

        while current_date <= end_date:
            self.requests.append(
                (
                    scrapy.Request,
                    {
                        "url": f"{BASE_URL}?firstDate={current_date.format('DD-MM-YYYY')}",
                        "meta": META_CALENDAR,
                    },
                )
            )

            current_date = current_date.shift(days=1)

    def handle_response(self, response: Response) -> None:
        handlers = parse_raceday_calendar(response)

        for handler in handlers:
            requests = [(scrapy.Request, {"url": handler["url"], "meta": META_RACEDAY})]

            self.racedays[handler["raceday_key"]] = AustraliaRaceday(
                raceday=handler["raceday"],
                # race_type=handler["race_type"],
                requests=requests,
            )


class AustraliaRaceday:
    def __init__(
        self,
        raceday,
        # race_type,
        requests,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        # self.race_type = race_type
        self.races = {}
        self.starters = {}
        self.requests = requests

    def return_raceday(self) -> dict:
        for race in self.races.values():
            racenumber = race.get_output_value("links")[0]["link"]

            for starter in self.starters[racenumber].values():
                starter["starter"].add_value("horse", starter["horse"].load_item())

                race.add_value("race_starters", starter["starter"].load_item())

            self.raceday.add_value("races", race.load_item())

        return self.raceday.load_item()

    def add_requests(self, requests: list[tuple]) -> None:
        self.requests.extend(requests)

    def add_race(self, race: ItemLoader, race_info: ItemLoader) -> None:
        race.add_value("race_info", race_info.load_item())

        self.races[race.get_output_value("links")[0]["link"]] = race

    def add_starter(
        self,
        link: str,
        starter: ItemLoader,
        horse: ItemLoader,
        registration: ItemLoader | None = None,
    ) -> None:
        name = horse.get_output_value("horse_info")["name"]

        key = "".join([x for x in name if x.isalpha()])

        if link not in self.starters:
            self.starters[link] = {}

        if key not in self.starters[link]:
            self.starters[link][key] = {"starter": starter, "horse": horse}

        if registration:
            self.starters[link][key]["horse"].add_value(
                "registrations", registration.load_item()
            )

    def handle_response(self, response: Response) -> None:
        if "/race-fields/" in response.url:
            urls = parse_races(response, self)
            requests = [
                (scrapy.Request, {"url": url, "meta": META_RACE}) for url in urls
            ]
            self.add_requests(requests)

        elif "/ausbreed/" in response.url:
            parse_ausbreed_race_result(response, self.starters)
