import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RaceLink
from .processor_functions import shorten_race_link


class GermanRaceLink(RaceLink):
    link = scrapy.Field(
        input_processor=MapCompose(shorten_race_link),
        output_processor=TakeFirst()
    )
