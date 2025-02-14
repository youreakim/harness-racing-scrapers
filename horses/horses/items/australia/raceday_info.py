import scrapy
from horses.items.base import RacedayInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_basic, handle_raceday_date


class AustralianRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(handle_raceday_date), output_processor=TakeFirst()
    )
    racetrack = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
