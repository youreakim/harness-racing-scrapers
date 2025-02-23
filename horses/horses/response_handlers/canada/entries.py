import string

import arrow
import scrapy
from horses.parsers.canada.entries.stdbca import parse_races, parse_starters

CANADA_DOMAINS = ["standardbredcanada.ca"]


class CanadaCalendar:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.racedays = {}
        self.allowed_domains = CANADA_DOMAINS

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"https://standardbredcanada.ca/racing?active_tab=entries&entries_horse_letter={letter}",
                },
            )
            for letter in string.ascii_uppercase
        ]

    def handle_response(self, response):
        starters = parse_starters(response)

        for starter in starters:
            if (
                arrow.now().date()
                > arrow.get(
                    starter["raceday"].get_output_value("raceday_info")["date"]
                ).date()
            ):
                continue

            if starter["raceday"].get_output_value("links")[0]["link"] in self.racedays:
                raceday_parser = self.racedays[
                    starter["raceday"].get_output_value("links")[0]["link"]
                ]
            else:
                raceday_parser = CanadaRaceday(starter["raceday"])

                request = (
                    scrapy.Request,
                    {
                        "url": f"https://standardbredcanada.ca/racing/entries/data/{starter['raceday'].get_output_value('links')[0]['link']}",
                    },
                )

                raceday_parser.add_request(request)

                self.racedays[
                    starter["raceday"].get_output_value("links")[0]["link"]
                ] = raceday_parser

            raceday_parser.add_race(starter["race"], starter["race_info"])

            raceday_parser.add_starter(
                starter["race_info"].get_output_value("racenumber"),
                starter["starter"],
                starter["starter_info"],
                starter["horse"],
            )


class CanadaRaceday:
    def __init__(self, raceday, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.raceday = raceday
        self.races = {}
        self.starters = {}
        self.requests = []
        self.allowed_domains = CANADA_DOMAINS
        self.is_final = True

    def handle_response(self, response):
        if "Final Changes NOT Made" in response.text:
            self.is_final = False
        else:
            parse_races(response, self.raceday, self.races, self.starters)

    def add_request(self, request):
        self.requests.append(request)

    def add_race(self, race, race_info):
        racenumber = race_info.get_output_value("racenumber")

        if racenumber not in self.races:
            self.races[racenumber] = {"race": race, "race_info": race_info}

    def add_starter(self, racenumber, starter, starter_info, horse):
        name = horse.get_output_value("horse_info")["name"]

        key = "".join(x for x in name if x.isalpha())

        if racenumber not in self.starters:
            self.starters[racenumber] = {}

        if key not in self.starters[racenumber]:
            self.starters[racenumber][key] = {
                "starter": starter,
                "starter_info": starter_info,
                "horse": horse,
            }

    def return_raceday(self):
        return self.raceday.load_item() if self.is_final else None
