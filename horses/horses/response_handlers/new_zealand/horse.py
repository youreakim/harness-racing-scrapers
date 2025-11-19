import scrapy
from scrapy.http.response import Response
from horses.items.new_zealand import NZHorse
from horses.parsers.new_zealand.horse.hrnz import (
    parse_dam_offspring,
    parse_dam_sire_offspring,
    parse_horse_info,
    parse_pedigree,
    parse_sire_offspring,
    parse_starts,
)
from itemloaders import ItemLoader


NZ_DOMAINS = ["hrnz.co.nz"]


class NZHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = NZ_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"https://harness.hrnz.co.nz/gws/ws/r/infohorsews/wsd06x"
                            f"?Arg=hrnzg-Ptype&Arg=HorseSearch&Arg=hrnzg-DoSearch&Arg=TRUE"
                            f"&Arg=hrnzg-rSite&Arg=TRUE&Arg=hrnzg-SearchType&Arg=Horse"
                            f"&Arg=hrnzg-HorseName&Arg={self.name}",
                },
            )
        ]

    def handle_response(self, response: Response) -> None:
        self.parse_search_result(response)

    def parse_search_result(self, response: Response) -> None:
        if response.xpath("//h1[contains(text(),'Horse')]"):
            # We have multiple horses
            for row in response.xpath("//td/a[contains(@href,'Arg=HorseDetails')]"):
                link = row.xpath("./@href").get()

                link_splits = link.split("&Arg=")

                self.horses.append(NZHorseHandler(horse_id=link_splits[-3]))
        else:
            horse = parse_horse_info(response)

            horse_id = horse.get_output_value("registrations")[0]["link"]

            self.horses.append(NZHorseHandler(horse_id=horse_id, horse=horse))


class NZHorseHandler:
    def __init__(self, horse_id: str, horse: ItemLoader | None = None) -> None:
        self.horse_id = horse_id
        self.horse = horse or ItemLoader(item=NZHorse())

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"https://harness.hrnz.co.nz/gws/ws/r/infohorsews/wsd06x?Arg="
                    f"hrnzg-Ptype&Arg=HorsePedigree&Arg=hrnzg-HorseID&Arg={self.horse_id}"
                    f"&Arg=hrnzg-PerformanceType&Arg=A&Arg=hrnzg-RaceType&Arg=O"
                    f"&Arg=hrnzg-DoSearch&Arg=FALSE{self.horse_id}&Arg=hrnzg-rSite&Arg=TRUE"
                },
            ),
        ]

        if not horse:
            self.requests = [
                (
                    scrapy.Request,
                    {
                        "url": f"https://harness.hrnz.co.nz/gws/ws/r/infohorsews/wsd06x"
                        f"?Arg=hrnzg-Ptype&Arg=HorseDetails&Arg=hrnzg-DoSearch&Arg=TRUE"
                        f"&Arg=hrnzg-HorseId&Arg={self.horse_id}&Arg=hrnzg-rSite&Arg=TRUE"
                    },
                ),
                *self.requests,
            ]

    def handle_response(self, response: Response) -> None:
        if "HorseDetails" in response.url:
            parse_horse_info(response, self.horse)
            # self.parse_horse_info(response)
        elif "HorsePedigree" in response.url:
            parse_pedigree(response, self.horse)
            self.add_requests(response)
        elif "DamSireProgeny" in response.url:
            # pass
            dams = parse_dam_sire_offspring(response)

            for dam in dams:
                self.horse.add_value("offspring", dam.load_item())
        elif "SireProgeny" in response.url:
            parse_sire_offspring(response, self.horse)
        elif "MAREPROGENY" in response.url:
            parse_dam_offspring(response, self.horse)
        elif "HorseStarts" in response.url:
            parse_starts(response, self.horse)

    def return_horse(self) -> dict:
        return self.horse.load_item()

    def add_requests(self, response: Response) -> None:
        page_list = ["Progeny", "Dam Sire Progeny", "Race Starts"]

        for list_item in response.xpath("//div[@id='quick-links-list']//a"):
            if list_item.xpath("./text()").get().strip() in page_list:
                self.requests.append(
                    (
                        scrapy.Request,
                        {
                            "url": f"https://harness.hrnz.co.nz{list_item.xpath('./@href').get()}"
                        },
                    )
                )
