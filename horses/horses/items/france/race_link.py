import scrapy
from itemloaders.processors import MapCompose, Join

from horses.items.base import RaceLink
from .processor_functions import shorten_race_link


class FrenchRaceLink(RaceLink):
    link = scrapy.Field(
        input_processor=MapCompose(shorten_race_link),
        output_processor=Join('/')
    )
