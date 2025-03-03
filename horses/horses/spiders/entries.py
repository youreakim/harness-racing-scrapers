import scrapy
from horses.response_handlers.australia.entries import AustraliaCalendar
from horses.response_handlers.belgium.entries import BelgiumCalendar
from horses.response_handlers.canada.entries import CanadaCalendar
from horses.response_handlers.denmark.entries import DenmarkCalendar
from horses.response_handlers.finland.entries import FinlandCalendar
from horses.response_handlers.france.entries import FranceCalendar
from horses.response_handlers.germany.entries import GermanyCalendar
from horses.response_handlers.holland.entries import HollandCalendar

# from horses.response_handlers.italy.entries import ItalyCalendar
# from horses.response_handlers.new_zealand.entries import NZCalendar
# from horses.response_handlers.norway.entries import NorwayCalendar
# from horses.response_handlers.spain.entries import SpainCalendar
# from horses.response_handlers.sweden.entries import SwedenCalendar
# from horses.response_handlers.usa.entries import USCalendar


class EntriesSpider(scrapy.Spider):
    name = "entries"

    def __init__(self, country, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.racedays = []
        self.country = country

        self.handler = {
            "australia": AustraliaCalendar,
            "belgium": BelgiumCalendar,
            "canada": CanadaCalendar,
            "denmark": DenmarkCalendar,
            "finland": FinlandCalendar,
            "france": FranceCalendar,
            "germany": GermanyCalendar,
            "holland": HollandCalendar,
            # "italy": ItalyCalendar,
            # "nz": NZCalendar,
            # "norway": NorwayCalendar,
            # "spain": SpainCalendar,
            # "sweden": SwedenCalendar,
            # "usa": USCalendar,
        }[country]()

        self.allowed_domains = self.handler.allowed_domains

    def start_requests(self):
        req, req_params = self.handler.requests.pop(0)

        yield req(callback=self.handle_calendar, **req_params)

    async def handle_calendar(self, response):
        if self.country == "usa":
            await self.handler.handle_response(response)

            return

        page = response.meta.get("playwright_page", None)

        if page:
            await page.close()

        self.handler.handle_response(response)

        if len(self.handler.requests) == 0:
            for raceday_handler in self.handler.racedays.values():
                req, req_params = raceday_handler.requests.pop(0)

                yield req(
                    callback=self.handle_raceday,
                    cb_kwargs={"raceday_handler": raceday_handler},
                    **req_params,
                )
        else:
            req, req_params = self.handler.requests.pop(0)

            yield req(callback=self.handle_calendar, **req_params)

    async def handle_raceday(self, response, raceday_handler):
        page = response.meta.get("playwright_page", None)

        if page:
            await page.close()

        raceday_handler.handle_response(response)

        if len(raceday_handler.requests) == 0:
            yield raceday_handler.return_raceday()
        else:
            req, req_params = raceday_handler.requests.pop(0)

            yield req(
                callback=self.handle_raceday,
                cb_kwargs={"raceday_handler": raceday_handler},
                **req_params,
            )
