import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose

from horses.items.base import RaceTime
from .processor_functions import handle_race_time


class AustralianRaceTime(RaceTime):
    at_distance = scrapy.Field(
        input_processor=MapCompose(round),
        output_processor=TakeFirst()
    )
    time = scrapy.Field(
        input_processor=MapCompose(handle_race_time),
        output_processor=Compose(lambda v: round(sum(v), ndigits=1))
    )
