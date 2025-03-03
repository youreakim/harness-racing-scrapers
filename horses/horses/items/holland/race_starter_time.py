import scrapy
from horses.items.base import RaceStarterTime
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_time


class DutchRaceStarterTime(RaceStarterTime):
    time = scrapy.Field(
        input_processor=MapCompose(handle_time), output_processor=TakeFirst()
    )
