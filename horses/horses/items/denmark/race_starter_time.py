import scrapy
from horses.items.base import RaceStarterTime
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_distance, handle_racetime


class DanishRaceStarterTime(RaceStarterTime):
    from_distance = scrapy.Field(
        input_processor=MapCompose(handle_distance), output_processor=TakeFirst()
    )
    time = scrapy.Field(
        input_processor=MapCompose(handle_racetime), output_processor=TakeFirst()
    )
    to_distance = scrapy.Field(
        input_processor=MapCompose(handle_distance), output_processor=TakeFirst()
    )
