import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RaceLink
from .processor_functions import handle_racelink


class BelgianRaceLink(RaceLink):
    link = scrapy.Field(
        input_processor=MapCompose(handle_racelink),
        output_processor=TakeFirst()
    )
