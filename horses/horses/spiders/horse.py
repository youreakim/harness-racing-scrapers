from typing import Any

import scrapy
from horses.response_handlers.australia.horse import AustraliaHorseSearch
from horses.response_handlers.denmark.horse import DenmarkHorseSearch
from horses.response_handlers.finland.horse import FinlandHorseSearch
from horses.response_handlers.france.horse import FranceHorseSearch
from horses.response_handlers.germany.horse import GermanyHorseSearch
from horses.response_handlers.holland.horse import HollandHorseSearch
from horses.response_handlers.italy.horse import ItalyHorseSearch
from horses.response_handlers.new_zealand.horse import NZHorseSearch
from horses.response_handlers.norway.horse import NorwayHorseSearch
from horses.response_handlers.spain.horse import SpainHorseSearch
from horses.response_handlers.sweden.horse import SwedenHorseSearch

# from horses.response_handlers.belgium.horse import BelgiumHorseSearch
# from horses.response_handlers.canada.horse import CanadaHorseSearch
# from horses.response_handlers.usa.horse import USHorseSearch


class HorseSpider(scrapy.Spider):
    name = "horse"

    def __init__(self, country: str, horse_name: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.horse_name = horse_name
        self.country = country
        self.handler = {
            "australia": AustraliaHorseSearch,
            # "belgium": BelgiumHorseSearch,
            # "canada": CanadaHorseSearch,
            "denmark": DenmarkHorseSearch,
            "finland": FinlandHorseSearch,
            "france": FranceHorseSearch,
            "germany": GermanyHorseSearch,
            "holland": HollandHorseSearch,
            "italy": ItalyHorseSearch,
            "new zealand": NZHorseSearch,
            "norway": NorwayHorseSearch,
            "spain": SpainHorseSearch,
            "sweden": SwedenHorseSearch,
            # "usa": USHorseSearch,
        }[country](self.horse_name)

        self.allowed_domains = self.handler.allowed_domains

    def start_requests(self):
        req, req_params = self.handler.requests.pop(0)

        yield req(callback=self.handle_search_result, **req_params)

    async def handle_search_result(self, response):
        page = response.meta.get("playwright_page", None)

        if page:
            await page.close()

        self.handler.handle_response(response)

        if len(self.handler.requests) != 0:
            req, req_params = self.handler.requests.pop(0)

            yield req(callback=self.handle_search_result, **req_params)

        else:
            for horse_handler in self.handler.horses:
                if len(horse_handler.requests) == 0:
                    yield horse_handler.return_horse()
                    continue

                req, req_params = horse_handler.requests.pop(0)

                yield req(
                    callback=self.handle_horse,
                    cb_kwargs={"horse_handler": horse_handler},
                    **req_params,
                )

    async def handle_horse(self, response, horse_handler):
        page = response.meta.get("playwright_page", None)

        if page:
            await page.close()

        horse_handler.handle_response(response)

        if len(horse_handler.requests) == 0:
            yield horse_handler.return_horse()

        else:
            req, req_params = horse_handler.requests.pop(0)

            yield req(
                callback=self.handle_horse,
                cb_kwargs={"horse_handler": horse_handler},
                **req_params,
            )
