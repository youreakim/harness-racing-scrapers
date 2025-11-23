import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RaceTime
from .processor_functions import handle_racetime


class SpanishRaceTime(RaceTime):
    time = scrapy.Field(
        input_processor=MapCompose(handle_racetime),
        output_processor=TakeFirst()
    )
