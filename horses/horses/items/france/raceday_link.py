import scrapy
from itemloaders.processors import MapCompose, Join

from horses.items.base import RacedayLink
from .processor_functions import shorten_raceday_link


class FrenchRacedayLink(RacedayLink):
    link = scrapy.Field(
        input_processor=MapCompose(shorten_raceday_link),
        output_processor=Join(separator='/')
    )
