import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RaceLink


class SwedishRaceLink(RaceLink):
    link = scrapy.Field(
        input_processor=MapCompose(str),
        output_processor=TakeFirst()
    )
