import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RacedayLink
from .processor_functions import shorten_raceday_link


class GermanRacedayLink(RacedayLink):
    link = scrapy.Field(
        input_processor=MapCompose(shorten_raceday_link),
        output_processor=TakeFirst()
    )
