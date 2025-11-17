import arrow
import scrapy
from horses.items.italy import (
    ItalianHorse,
    ItalianRace,
    ItalianRaceday,
    ItalianRaceStarter,
    ItalianRaceStarterOdds,
)
from horses.parsers.italy.results.anact import parse_anact_calendar
from horses.parsers.italy.results.snai import parse_snai_calendar, parse_snai_race, parse_snai_starter
from horses.parsers.italy.results.trottoweb import (
    parse_trottoweb_calendar,
    parse_trottoweb_races,
)
from horses.parsers.italy.results.unire import parse_unire_calendar, parse_unire_race
from itemloaders import ItemLoader
from scrapy_playwright.page import PageMethod
from scrapy.http.response import Response

ITALIAN_DOMAINS = ["anact.it", "unire.gov.it",
                   "ippica.snai.it", "trottoweb.it"]
ITALIAN_META_ANACT = {
    'playwright': True,
    'playwright_include_page': True,
    'playwright_page_methods': [
        PageMethod('wait_for_selector', '//div[contains(@class,"ippodromo")]'),
    ]
}
ITALIAN_META_SNAI = {
    "playwright": True,
    "playwright_include_page": True,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "div.message.is-snai-1")
    ],
}
ITALIAN_META_UNIRE = {
    "playwright": True,
    "playwright_include_page": True,
    "playwright_page_methods": [PageMethod("wait_for_selector", "tr.mainline")],
}
ITALIAN_META_TROTTOWEB = {
    "playwright": True,
    "playwright_include_page": True,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "div.ippodromi-event"),
    ],
}
META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_ANACT_CALENDAR = {}
META_SNAI_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "div.message.is-snai-1")
    ],
}
META_SNAI_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//a[contains(@href,"prestazioni")]')
    ],
}
META_UNIRE_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "tr.mainline")],
}
META_UNIRE_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [PageMethod("wait_for_selector", "//table//a")],
}
META_TROTTOWEB_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "//td[@class='dati_ippo']"),
    ],
}
META_TROTTOWEB_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", "//div[@id='dati_corsa']")
    ],
}


class ItalyCalendar:
    def __init__(self, start_date, end_date, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.start_date = start_date
        self.end_date = end_date
        self.current_raceday = None
        self.allowed_domains = ITALIAN_DOMAINS

        self.requests = []

        for date in arrow.Arrow.range("days", self.start_date, self.end_date):
            self.requests.append(
                (
                    scrapy.Request,
                    {
                        "url": f"https://www.anact.it/risultato-corsa/?giornata={date.date().isoformat()}",
                        "meta": META_ANACT_CALENDAR
                    },
                )
            )

        current_date = self.start_date

        while current_date.date() <= self.end_date.date():
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

        ippica_min_date = arrow.utcnow().shift(years=-10).floor("year")

        if self.end_date.date() >= ippica_min_date.date():
            ip_start_date = (
                self.start_date
                if self.start_date.date() >= ippica_min_date.date()
                else ippica_min_date
            )

            for date in arrow.Arrow.range("days", ip_start_date, self.end_date):
                self.requests.append(
                    (
                        scrapy.Request,
                        {
                            "url": f"https://ippica.snai.it/risultati/{date.date().isoformat()}"
                        },
                    )
                )

        unire_min_date = arrow.utcnow().shift(days=-3)

        if self.end_date >= unire_min_date:
            self.requests.append(
                (
                    scrapy.FormRequest,
                    {
                        "url": "https://www.unire.gov.it/index.php/ita/notizario/list/oggi/1",
                        "meta": META_UNIRE_CALENDAR,
                        "formdata": {"giornate": "Giornate+precedenti"},
                    },
                )
            )

    def handle_response(self, response: Response) -> None:
        if "anact" in response.url:
            self.parse_anact_calendar(response)
        elif "snai" in response.url:
            self.parse_snai_calendar(response)
        elif "unire" in response.url:
            self.parse_unire_calendar(response)
        elif "trottoweb" in response.url:
            self.parse_trottoweb_calendar(response)

    def parse_anact_calendar(self, response: Response) -> None:
        racedays = parse_anact_calendar(response, response.url.split("=")[1])

        for raceday in racedays:
            raceday_parser = ItalyRaceday(raceday=raceday['raceday'])

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


    def parse_snai_calendar(self, response: Response) -> None:
        racedays = parse_snai_calendar(response)

        for raceday in racedays:
            if raceday['key'] in self.racedays:
                self.racedays[raceday['key']].add_raceday_link(raceday['raceday_link'])
            else:
                r = ItemLoader(item=ItalianRaceday())

                r.add_value('raceday_info', raceday['raceday_info'])
                r.add_value('links', raceday['raceday_link'])

                self.racedays[raceday['key']] = ItalyRaceday(raceday=r)

            self.racedays[raceday['key']].add_requests(
                (scrapy.Request, {"url": url, "meta": META_SNAI_RACE})
                for url in raceday['race_links']
            )

    def parse_unire_calendar(self, response: Response) -> None:
        racedays = parse_unire_calendar(response, self.start_date, self.end_date)

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
        racedays = parse_trottoweb_calendar(response, self.start_date, self.end_date)

        for raceday in racedays:
            if raceday["key"] in self.racedays:
                self.racedays[raceday["key"]].add_raceday_link(raceday['raceday_link'])
            else:
                r = ItemLoader(item=ItalianRaceday())

                r.add_value('raceday_info', raceday['raceday_info'])
                r.add_value('links', raceday['raceday_link'])

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
        self, raceday: ItemLoader, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.races = {}
        self.starters = {}
        self.requests = []

    def handle_response(self, response: Response) -> None:
        if "snai" in response.url:
            self.parse_snai_race(response)
        elif "unire" in response.url:
            if "list/riunione" in response.url:
                self.parse_unire_raceday(response)
            else:
                self.parse_unire_race(response)
        elif "trottoweb" in response.url:
            self.parse_trottoweb_raceday(response)

    def add_raceday_link(self, raceday_link: ItemLoader) -> None:
        self.raceday.add_value("links", raceday_link.load_item())

    def add_requests(self, requests: list[tuple]) -> None:
        self.requests.extend(requests)

    def add_race(
        self,
        race_info: ItemLoader,
        race_link: ItemLoader|None=None
    ) -> None:
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
        registration: ItemLoader,
        times:list[ItemLoader]=[],
        odds:list[ItemLoader]=[]
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
                "times": [x.load_item() for x in times]
            }
        else:
            for k, v in horse_info.load_item().items():
                self.starters[racenumber][key]["horse_info"].add_value(k, v)

            for k, v in starter_info.load_item().items():
                self.starters[racenumber][key]["starter_info"].add_value(k, v)

        self.starters[racenumber][key]["horse"].add_value("registrations", registration.load_item())

        for o in odds:
            self.starters[racenumber][key]["starter"].add_value("odds", o)

    def return_raceday(self) -> dict:
        for racenumber, race in self.races.items():
            race["race"].add_value("race_info", race["race_info"].load_item())

            for starter in self.starters[racenumber].values():
                starter["starter"].add_value("starter_info", starter["starter_info"].load_item())
                starter["horse"].add_value("horse_info", starter["horse_info"].load_item())
                starter["starter"].add_value("horse", starter["horse"].load_item())

                done = []

                for time in starter["times"]:
                    if [time["from_distance"], time["to_distance"]] not in done:
                        starter["starter"].add_value("times", time)
                        done.append([time["from_distance"], time["to_distance"]])

                race["race"].add_value("race_starters", starter["starter"].load_item())

            self.raceday.add_value("races", race["race"].load_item())

        return self.raceday.load_item()

    def parse_snai_race(self, response: Response) -> None:
        race = parse_snai_race(response)

        self.add_race(race["race_info"], race["race_link"])

        odds_string = response.xpath('//span[contains(@class,"tag-quota-piaz")]//following-sibling::text()').get().strip()

        place_odds = {}

        while odds_string != '':
            startnumber = odds_string[odds_string.find('(') + 1: odds_string.find(')')]
            odds = odds_string[:odds_string.find(' ')]

            o = ItemLoader(item=ItalianRaceStarterOdds())

            o.add_value('odds', odds.replace(",", "."))
            o.add_value('odds_type', 'show')

            if startnumber in place_odds:
                place_odds[startnumber].append(o.load_item())
            else:
                place_odds[startnumber] = [o.load_item()]

            odds_string = odds_string[odds_string.find(')') + 1:].strip()

        raceday_date = self.raceday.get_output_value("raceday_info")["date"]

        for order, starter_row in enumerate(
            response.xpath(
                '//div[contains(@class,"message")][1]//div[contains(@class,"list-group-item-condensed")]'
            ),
            1,
        ):
            starter = parse_snai_starter(starter_row, order, int(raceday_date[:4]), place_odds)

            self.add_starter(race["race_info"].get_output_value("racenumber"), **starter)

    def parse_unire_raceday(self, response: Response) -> None:
        self.add_requests(
            [(
                scrapy.Request,
                {"url": f"https://www.unire.gov.it{url}", "meta": META_UNIRE_RACE},
            )
            for url in response.xpath("//table//a/@href").getall()]
        )

    def parse_unire_race(self, response: Response) -> None:
        race = parse_unire_race(response)

        self.add_race(race["race_info"], race["race_link"])

        for starter in race["starters"]:
            self.add_starter(
                race["race_info"].get_output_value("racenumber"), **starter
            )

    def parse_trottoweb_raceday(self, response: Response) -> None:
        races = parse_trottoweb_races(response)

        for race in races:
            self.add_race(race["race_info"], race["race_link"])

            for starter in race["starters"]:
                self.add_starter(
                    race["race_info"].get_output_value("racenumber"), **starter
                )
