import scrapy
from horses.items.base import RaceLink
from itemloaders.processors import MapCompose, TakeFirst


class DanishRaceLink(RaceLink):
    link = scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
