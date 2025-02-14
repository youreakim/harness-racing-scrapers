import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import RacedayLink
from .processor_functions import shorten_raceday_link


class AustralianRacedayLink(RacedayLink):
    link = scrapy.Field(
        input_processor=MapCompose(shorten_raceday_link),
        output_processor=TakeFirst()
    )
