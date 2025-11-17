import arrow
import scrapy
from horses.parsers.italy.entries.anact import parse_anact_calendar
from horses.parsers.italy.entries.trottoweb import (
    parse_trottoweb_calendar,
    parse_trottoweb_races,
)
from horses.parsers.italy.entries.unire import (
    parse_unire_calendar,
    parse_unire_race,
    parse_unire_race_links,
)
from horses.items.italy import (
    ItalianHorse,
    ItalianRace,
    ItalianRaceday,
    ItalianRaceStarter,
)
from itemloaders import ItemLoader
from scrapy.http.response import Response
from scrapy_playwright.page import PageMethod

ITALIAN_DOMAINS = ["anact.it", "unire.gov.it",
                   "ippica.snai.it", "trottoweb.it"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_PLAYWRIGHT_ANACT = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod(
            "wait_for_selector",
            "//div[contains(@class,'ippodromo')]/span"
        )
    ]
}
META_UNIRE_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "tr.mainline")],
}
META_UNIRE_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "//table//a")],
}


class ItalyCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.allowed_domains = ITALIAN_DOMAINS

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": "https://www.anact.it/partente-corsa/", "meta": META_PLAYWRIGHT_ANACT
                }
            ),
            (
                scrapy.FormRequest,
                {
                    "url": "https://www.unire.gov.it/index.php/ita/notizario/list/oggi/1",
                    "formdata": {"prossime": "Prossime+giornate"},
                    "meta": META_UNIRE_CALENDAR
                },
            ),
        ]

        end_date = arrow.utcnow().shift(days=6)

        current_date = end_date

        while current_date.date() <= end_date.date():
            self.requests.append(
                (
                    scrapy.FormRequest,
                    {
                        "url": "https://www.trottoweb.it/TrottoWeb/php/hCal.php",
                        "formdata": {
                            "eventi": "TT",
                            "anno": f"{current_date.year}",
                            "mese": f"{current_date.month}",
                            "ippod": "TT",
                        },
                    },
                )
            )

            current_date = current_date.shift(months=1).floor("month")

    def handle_response(self, response: Response) -> None:
        if "anact" in response.url:
            self.parse_anact_calendar(response)
        elif "unire" in response.url:
            self.parse_unire_calendar(response)
        elif "trottoweb" in response.url:
            self.parse_trottoweb_calendar(response)

    def parse_anact_calendar(self, response: Response) -> None:
        racedays = parse_anact_calendar(response)

        for raceday in racedays:
            raceday_parser = ItalyRaceday(raceday=raceday["raceday"])

            for race in raceday["races"]:
                raceday_parser.add_race(race["race_info"], race["race_link"])

                _ = [
                    raceday_parser.add_starter(
                        race["race_info"].get_output_value(
                            "racenumber"), **starter
                    )
                    for starter in race["starters"]
                ]

            self.racedays[raceday["key"]] = raceday_parser

    def parse_unire_calendar(self, response: Response) -> None:
        racedays = parse_unire_calendar(response)

        for raceday in racedays:
            if raceday['key'] in self.racedays:
                self.racedays[raceday['key']].add_raceday_link(raceday['raceday_link'])
            else:
                r = ItemLoader(item=ItalianRaceday())

                r.add_value('raceday_info', raceday['raceday_info'].load_item())
                r.add_value('links', raceday['raceday_link'].load_item())

                self.racedays[raceday['key']] = ItalyRaceday(raceday=r)

            self.racedays[raceday['key']].add_requests(
                [
                    (
                        scrapy.Request,
                        {'url': f'https://www.unire.gov.it/{raceday["raceday_link"].get_output_value("link")}',
                        "meta": META_UNIRE_RACE,}
                    )
                ]
            )

    def parse_trottoweb_calendar(self, response: Response) -> None:
        racedays = parse_trottoweb_calendar(response)

        for raceday in racedays:
            if raceday["key"] in self.racedays:
                self.racedays[raceday["key"]].add_raceday_link(raceday['raceday_link'])
            else:
                r = ItemLoader(item=ItalianRaceday())

                r.add_value('raceday_info', raceday['raceday_info'].load_item())
                r.add_value('links', raceday['raceday_link'].load_item())

                self.racedays[raceday['key']] = ItalyRaceday(raceday=r)

            self.racedays[raceday["key"]].add_requests(
                [
                    (
                        scrapy.Request,
                        {"url": raceday["url"]},
                    )
                ]
            )


class ItalyRaceday:
    def __init__(
        self,
        raceday: ItemLoader,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.races = {}
        self.starters = {}
        self.requests = []

    def handle_response(self, response: Response) -> None:
        if "trottoweb" in response.url:
            races = parse_trottoweb_races(response)

            for race in races:
                self.add_race(race["race_info"], race["race_link"])

                for starter in race["starters"]:
                    self.add_starter(
                        race["race_info"].get_output_value("racenumber"), **starter
                    )

        elif "list/riunione" in response.url:
            self.add_requests([
                (
                    scrapy.Request,
                    {
                        "url": f"https://www.unire.gov.it{link}",
                    },
                )
                for link in parse_unire_race_links(response)
            ])
        else:
            race = parse_unire_race(response)

            self.add_race(race["race_info"], race["race_link"])

            for starter in race["starters"]:
                self.add_starter(
                    race["race_info"].get_output_value("racenumber"), **starter
                )

    def add_raceday_link(self, raceday_link: ItemLoader) -> None:
        self.raceday.add_value("links", raceday_link.load_item())

    def add_requests(self, requests: list[tuple]) -> None:
        self.requests.extend(requests)

    def add_race(self, race_info: ItemLoader, race_link: ItemLoader|None=None) -> None:
        racenumber = race_info.get_output_value("racenumber")

        if racenumber in self.races:
            r = race_info.load_item()

            for key, value in r.items():
                self.races[racenumber]["race_info"].add_value(key, value)

            if race_link is not None:
                self.races[racenumber]["race"].add_value("links", race_link.load_item())
        else:
            race = ItemLoader(item=ItalianRace())

            if race_link is not None:
                race.add_value("links", race_link.load_item())

            self.races[racenumber] = {'race': race, 'race_info': race_info}

    def add_starter(
        self,
        racenumber: int,
        starter_info: ItemLoader,
        horse_info: ItemLoader,
        registration: ItemLoader
    ) -> None:
        if racenumber not in self.starters:
            self.starters[racenumber] = {}

        key = "".join(x for x in horse_info.get_output_value("name"))

        if key not in self.starters[racenumber]:
            self.starters[racenumber][key] = {
                "starter": ItemLoader(item=ItalianRaceStarter()),
                "horse": ItemLoader(item=ItalianHorse()),
                "horse_info": horse_info,
                "starter_info": starter_info,
            }
        else:
            for k, v in horse_info.load_item().items():
                self.starters[racenumber][key]["horse_info"].add_value(k, v)

            for k, v in starter_info.load_item().items():
                self.starters[racenumber][key]["starter_info"].add_value(k, v)

        if registration is not None:
            self.starters[racenumber][key]["horse"].add_value("registrations", registration.load_item())

    def return_raceday(self) -> dict:
        for racenumber, race in self.races.items():
            race["race"].add_value("race_info", race["race_info"].load_item())

            for starter in self.starters[racenumber].values():
                starter["starter"].add_value("starter_info", starter["starter_info"].load_item())
                starter["horse"].add_value("horse_info", starter["horse_info"].load_item())
                starter["starter"].add_value("horse", starter["horse"].load_item())

                race["race"].add_value("race_starters", starter["starter"].load_item())

            self.raceday.add_value("races", race["race"].load_item())

        return self.raceday.load_item()
