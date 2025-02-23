import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RaceTime
from .processor_functions import handle_starter_time


class CanadianRaceTime(RaceTime):
    time = scrapy.Field(
        input_processor=MapCompose(handle_starter_time),
        output_processor=TakeFirst()
    )
