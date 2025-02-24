from typing import Iterable

import arrow
import scrapy
from horses.response_handlers.australia.results import AustraliaCalendar
from horses.response_handlers.belgium.results import BelgiumCalendar
from horses.response_handlers.canada.results import CanadaCalendar
from horses.response_handlers.denmark.results import DenmarkCalendar

# from horses.response_handlers.finland.results import FinlandCalendar
# from horses.response_handlers.france.results import FranceCalendar
# from horses.response_handlers.germany.results import GermanyCalendar
# from horses.response_handlers.holland.results import HollandCalendar
# from horses.response_handlers.italy.results import ItalyCalendar
# from horses.response_handlers.new_zealand.results import NZCalendar
# from horses.response_handlers.norway.results import NorwayCalendar
# from horses.response_handlers.spain.results import SpainCalendar
# from horses.response_handlers.sweden.results import SwedenCalendar
# from horses.response_handlers.usa.results import USCalendar
from scrapy.http.response import Response


class ResultSpider(scrapy.Spider):
    name = "results"

    def __init__(
        self,
        country: str,
        *args,
        start_date: str | None = None,
        end_date: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.racedays = []
        self.country = country

        self.start_date = (
            arrow.utcnow().shift(days=-1)
            if start_date is None
            else arrow.get(start_date, "YYYY-MM-DD")
        )
        self.end_date = (
            arrow.utcnow().shift(days=-1)
            if end_date is None
            else arrow.get(end_date, "YYYY-MM-DD")
        )

        self.handler = {
            "australia": AustraliaCalendar,
            "belgium": BelgiumCalendar,
            "canada": CanadaCalendar,
            "denmark": DenmarkCalendar,
            # "finland": FinlandCalendar,
            # "france": FranceCalendar,
            # "germany": GermanyCalendar,
            # "holland": HollandCalendar,
            # "italy": ItalyCalendar,
            # "nz": NZCalendar,
            # "norway": NorwayCalendar,
            # "spain": SpainCalendar,
            # "sweden": SwedenCalendar,
            # "usa": USCalendar,
        }[country](self.start_date, self.end_date)

        self.allowed_domains = self.handler.allowed_domains

    def start_requests(self) -> Iterable[scrapy.Request]:
        req, req_params = self.handler.requests.pop(0)

        yield req(callback=self.handle_calendar, **req_params)

    async def handle_calendar(self, response: Response):
        if self.country == "usa":
            await self.handler.handle_response(response)

            return

        page = response.meta.get("playwright_page", None)

        if page:
            await page.close()

        self.handler.handle_response(response)

        if len(self.handler.requests) == 0:
            for raceday_handler in self.handler.racedays.values():
                if len(raceday_handler.requests) == 0:
                    yield raceday_handler.return_raceday()
                    continue

                req, req_params = raceday_handler.requests.pop(0)

                yield req(
                    callback=self.handle_raceday,
                    cb_kwargs={"raceday_handler": raceday_handler},
                    **req_params,
                )
        else:
            req, req_params = self.handler.requests.pop(0)

            yield req(callback=self.handle_calendar, **req_params)

    async def handle_raceday(self, response: Response, raceday_handler):
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
