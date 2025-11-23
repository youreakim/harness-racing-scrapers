import arrow
from itemloaders import ItemLoader
import scrapy
from scrapy.http.response import Response
from horses.parsers.spain.results.fect import (
    parse_calendar,
    parse_race_info,
    parse_race_links,
    parse_race_starters,
    parse_race_starters_pedigrees,
)
from scrapy_playwright.page import PageMethod

SPANISH_DOMAINS = ["federaciobaleardetrot.com", "astrot.com"]

META_PLAYWRIGHT = {"playwright": True, "playwright_include_page": True}
META_CALENDAR = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//td[@role="gridcell"]')
    ],
}
META_RACEDAY = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//table[@id="tabla_jornada"]')
    ],
}
META_CONDITIONS = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//div[@class="well"]')
    ],
}
META_RACE = {
    **META_PLAYWRIGHT,
    "playwright_page_methods": [
        PageMethod("wait_for_selector", '//table[contains(@id,"tabla_")]')
    ],
}


class SpainCalendar:
    def __init__(self, start_date: arrow.arrow.Arrow, end_date: arrow.arrow.Arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.requests = []
        self.start_date = start_date
        self.end_date = end_date
        self.allowed_domains = SPANISH_DOMAINS

        for year in range(self.start_date.year, self.end_date.year + 1):
            self.requests.append(
                (
                    scrapy.Request,
                    {
                        "url": f"https://www.federaciobaleardetrot.com/calendarioCarreras.php?anyo={year}",
                        "meta": META_CALENDAR,
                    },
                )
            )

    def handle_response(self, response: Response) -> None:
        self.parse_calendar(response)

    def parse_calendar(self, response: Response) -> None:
        racedays = parse_calendar(response, self.start_date, self.end_date)

        for raceday in racedays:
            requests = [(scrapy.Request, {"url": raceday["url"], "meta": META_RACEDAY})]

            self.racedays[raceday["key"]] = SpainRaceday(raceday=raceday["raceday"], requests=requests)


class SpainRaceday:
    def __init__(self, raceday: ItemLoader, requests:list|None=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.requests = requests if requests is not None else []
        self.races = {}
        self.starters = {}

    def handle_response(self, response: Response) -> None:
        if "Condiciones" in response.url:
            self.parse_race_info(response)

        elif "Tipo=3" in response.url:
            self.parse_race_starters_info(response)

        elif "Tipo=2" in response.url:
            self.parse_race_starters_pedigree(response)

        elif "idPrograma" in response.url:
            self.parse_race_links(response)

    def return_raceday(self) -> dict:
        for racenumber, race in self.races.items():
            for starter, horse in self.starters[racenumber].values():
                starter.add_value("horse", horse.load_item())

                race.add_value("race_starters", starter.load_item())

            self.raceday.add_value("races", race.load_item())

        return self.raceday.load_item()

    def parse_race_links(self, response: Response) -> None:
        links = parse_race_links(response)

        self.requests.extend([(
                scrapy.Request,
                {
                    "url": link,
                    "meta": META_CONDITIONS if link[-2] != "=" else META_RACE,
                },
            ) for link in links])

    def parse_race_info(self, response: Response) -> None:
        race = parse_race_info(response)

        self.races[race.get_output_value("race_info")["racenumber"]] = race

    def parse_race_starters_info(self, response: Response) -> None:
        starters = parse_race_starters(response)

        for starter in starters:
            if starter["racenumber"] not in self.starters:
                self.starters[starter["racenumber"]] = {}

            self.starters[starter["racenumber"]][starter["link"]] = (starter["starter"], starter["horse"])

    def parse_race_starters_pedigree(self, response: Response) -> None:
        pedigrees = parse_race_starters_pedigrees(response)

        for pedigree in pedigrees:
            starter, horse = self.starters[pedigree["racenumber"]][pedigree["link"]]

            horse.add_value("sire", pedigree["sire"].load_item())
            horse.add_value("dam", pedigree["dam"].load_item())

            starter.add_value("horse", horse.load_item())
