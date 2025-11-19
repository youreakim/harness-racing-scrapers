import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RacedayInfo
from .processor_functions import handle_date


class NZRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(handle_date),
        output_processor=TakeFirst()
    )
