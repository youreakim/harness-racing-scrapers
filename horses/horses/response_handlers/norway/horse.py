import scrapy
from scrapy.http.response import Response
from horses.items.norway import NorwegianHorse
from horses.parsers.norway.horse.dnt import parse_horse
from itemloaders import ItemLoader

NORWEGIAN_DOMAINS = ["travsport.no"]
NORWEGIAN_META = {"playwright": True, "playwright_include_page": True}


class NorwayHorseSearch:
    def __init__(self, name: str) -> None:
        self.allowed_domains = NORWEGIAN_DOMAINS
        self.name = name
        self.horses = []

        self.requests = [
            (
                scrapy.Request,
                {
                    "url": f"https://www.travsport.no/sportsbasen/sportssok/?q={self.name}"
                },
            )
        ]

    def handle_response(self, response: Response) -> dict | None:
        if "/?q=" in response.url:
            self.parse_search_result(response)
        else:
            horse = ItemLoader(item=NorwegianHorse())

            parse_horse(response, horse)

            self.horses.append(NorwayHorse('', horse))

    def parse_search_result(self, response: Response) -> None:
        for row in response.xpath("//tr/td/a/@href[contains(.,'/horse/')]]").get_all():
            horse_id = row[row.rfind("/") + 1 :]

            self.horses.append(NorwayHorse(horse_id=horse_id))


class NorwayHorse:
    def __init__(self, horse_id: str, horse: ItemLoader | None=None) -> None:
        self.horse_id = horse_id
        self.horse = ItemLoader(item=NorwegianHorse()) if horse is None else horse

        self.requests = [
            scrapy.Request,
            {
                "url": f"https://www.travsport.no/sportsbasen/sportssok/horse/{self.horse_id}"
            },
        ] if horse_id != '' else []

    def handle_response(self, response: Response) -> None:
        parse_horse(response, self.horse)

    def return_horse(self) -> dict:
        return self.horse.load_item()
