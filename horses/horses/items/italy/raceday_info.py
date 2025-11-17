import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RacedayInfo
from .processor_functions import handle_raceday_date, handle_racetrack


class ItalianRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(handle_raceday_date),
        output_processor=TakeFirst()
    )
    racetrack = scrapy.Field(
        input_processor=MapCompose(handle_racetrack),
        output_processor=TakeFirst()
    )
