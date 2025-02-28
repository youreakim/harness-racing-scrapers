import scrapy
from horses.items.base import RaceStarterTime
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_starter_time


class FrenchRaceStarterTime(RaceStarterTime):
    time = scrapy.Field(
        input_processor=MapCompose(handle_starter_time), output_processor=TakeFirst()
    )
