import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RacedayInfo
from .processor_functions import handle_date


class DutchRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(handle_date),
        output_processor=TakeFirst()
    )
