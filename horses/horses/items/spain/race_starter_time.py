import scrapy
from horses.items.base import RaceStarterTime
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_racetime


class SpanishRaceStarterTime(RaceStarterTime):
    time = scrapy.Field(
        input_processor=MapCompose(handle_racetime), output_processor=TakeFirst()
    )
