import arrow
from itemloaders import ItemLoader
import scrapy
from scrapy.http.response import Response
from horses.parsers.sweden.results.atg import parse_atg_calendar, parse_atg_race
from horses.parsers.sweden.results.st import parse_st_calendar, parse_st_raceday

SWEDISH_DOMAINS = ["travsport.se", "atg.se"]
ATG_BASE_URL = "https://www.atg.se/services/racinginfo/v1/api"
ST_BASE_URL = "https://api.travsport.se/webapi/raceinfo"
ST_CALENDAR_URL = f"{ST_BASE_URL}/organisation/TROT/sourceofdata/SPORT"
ST_RACEDAY_URL = f"{ST_BASE_URL}/results/organisation/TROT/sourceofdata/SPORT/racedayid/"


class SwedenCalendar:
    def __init__(self, start_date: arrow.arrow.Arrow, end_date: arrow.arrow.Arrow, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.races = {}
        self.requests = []
        self.allowed_domains = SWEDISH_DOMAINS

        self.start_date = start_date
        self.end_date = end_date

        current_date = self.start_date

        while current_date.date() <= self.end_date.date():
            self.requests = [
                (
                    scrapy.http.JsonRequest,
                    {
                        "url": f"{ST_CALENDAR_URL}?fromracedate={start_date.date().isoformat()}&"
                        f"tosubmissiondate={end_date.date().isoformat()}&toracedate={end_date.date().isoformat()}"
                    },
                )
            ]

            current_date = current_date.shift(months=1).floor("month")

        # ST stopped showing the odds on their site when 2019 started, fetch them at ATGs site
        if self.end_date.date() >= arrow.get("2019-01-01").date():
            atg_cal_start = (
                self.start_date
                if self.start_date.date() >= arrow.get("2019-01-01").date()
                else arrow.get("2019-01-01")
            )

            for date in arrow.Arrow.range("days", atg_cal_start, self.end_date):
                self.requests.append(
                    (
                        scrapy.http.JsonRequest,
                        {
                            "url": f"{ATG_BASE_URL}/calendar/day/{date.date().isoformat()}"
                        },
                    )
                )

    def handle_response(self, response: Response) -> None:
        if "travsport" in response.url:
            self.parse_st_calendar(response)
        else:
            self.parse_atg_calendar(response)

    def parse_st_calendar(self, response: Response) -> None:
        racedays = parse_st_calendar(response, self.start_date, self.end_date)

        for raceday in racedays:
            requests = [
                (
                    scrapy.http.JsonRequest,
                    {
                        "url": f"{ST_RACEDAY_URL}{raceday['raceday_id']}"
                    },
                )
            ]

            if raceday["key"] not in self.racedays:
                raceday["raceday"].add_value("links", raceday["raceday_link"].load_item())
                raceday["raceday"].add_value("raceday_info", raceday["raceday_info"].load_item())

                self.racedays[raceday["key"]] = SwedenRaceday(raceday=raceday["raceday"])
            else:
                self.racedays[raceday["key"]].raceday.add_value("links", raceday["raceday_link"].load_item())

            self.racedays[raceday["key"]].add_requests(requests)

    def parse_atg_calendar(self, response: Response) -> None:
        racedays = parse_atg_calendar(response)

        for raceday in racedays:
            requests = [
                    (
                        scrapy.http.JsonRequest,
                        {
                            "url": f"{ATG_BASE_URL}/games/vp_{raceday['date']}_"
                                f"{raceday['racetrack_id']}_{racenumber}"
                        },
                    ) for racenumber in range(1, raceday["races"] + 1)
                ]

            if raceday["key"] not in self.racedays:
                self.racedays[raceday["key"]] = SwedenRaceday(raceday=raceday["raceday"])

            self.racedays[raceday["key"]].add_requests(requests)


class SwedenRaceday:
    def __init__(self, raceday: ItemLoader, requests:list|None=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.races = {}
        self.starters = {}
        self.requests = requests if requests is not None else []

    def handle_response(self, response: Response) -> None:
        if "travsport" in response.url:
            self.parse_st_raceday(response)
        else:
            self.parse_atg_race(response)

    def add_requests(self, requests: list) -> None:
        self.requests.extend(requests)

    def return_raceday(self) -> dict:
        for racenumber, race in self.races.items():
            for starter in self.starters[racenumber].values():
                starter["starter"].add_value(
                    "starter_info", starter["starter_info"].load_item()
                )

                starter["horse"].add_value("horse_info", starter["horse_info"].load_item())
                starter["horse"].add_value("registrations", starter["registration"].load_item())
                
                if "sire" in starter:
                    starter["horse"].add_value("sire", starter["sire"].load_item())
                
                if "dam" in starter:
                    starter["horse"].add_value("dam", starter["dam"].load_item())

                starter["starter"].add_value("horse", starter["horse"].load_item())

                if starter["starter_time"]:
                    starter["starter"].add_value("times", starter["starter_time"].load_item())

                if len(starter["odds"]) > 0:
                    starter["starter"].add_value("odds", starter["odds"])

                race["race"].add_value("race_starters", starter["starter"].load_item())

            race["race"].add_value("race_info", race["race_info"].load_item())

            self.raceday.add_value("races", race["race"].load_item())

        return self.raceday.load_item()

    def parse_st_raceday(self, response: Response) -> None:
        races = parse_st_raceday(response)

        for race in races:
            if race["racenumber"] not in self.races:
                self.races[race["racenumber"]] = {
                    "race": race["race"],
                    "race_info": race["race_info"]
                }
                
            self.races[race["racenumber"]]["race"].add_value("links", race["race_link"].load_item())

            if race["racenumber"] not in self.starters:
                self.starters[race["racenumber"]] = race["starters"]

    def parse_atg_race(self, response: Response) -> None:
        race = parse_atg_race(response)

        if race["racenumber"] not in self.races:
            self.races[race["racenumber"]] = {
                "race": race["race"],
                "race_info": race["race_info"]
            }
            
        self.races[race["racenumber"]]["race"].add_value("links", race["race_link"].load_item())

        if race["racenumber"] not in self.starters:
            self.starters[race["racenumber"]] = race["starters"]

        else:
            for horse_id, starter in race["starters"].items():
                s = self.starters[race["racenumber"]][horse_id]

                s["sire"] = starter["sire"]
                s["dam"] = starter["dam"]
                s["odds"] = starter["odds"]
