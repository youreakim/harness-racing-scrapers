import scrapy
from horses.items.base import RacedayInfo
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_racedate, handle_racetrack


class SpanishRacedayInfo(RacedayInfo):
    date = scrapy.Field(
        input_processor=MapCompose(handle_racedate), output_processor=TakeFirst()
    )
    racetrack = scrapy.Field(
        input_processor=MapCompose(handle_racetrack), output_processor=TakeFirst()
    )
