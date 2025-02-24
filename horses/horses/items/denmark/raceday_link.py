from horses.items.base import RacedayLink
from itemloaders.processors import MapCompose, TakeFirst
from scrapy.http.request import scrapy


class DanishRacedayLink(RacedayLink):
    link = scrapy.Field(input_processor=MapCompose(str), output_processor=TakeFirst())
