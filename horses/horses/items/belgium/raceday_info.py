import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RacedayInfo
from .processor_functions import handle_raceday_date


class BelgianRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(handle_raceday_date),
        output_processor=TakeFirst()
    )
