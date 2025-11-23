import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RaceLink
from .processor_functions import get_race_id


class SpanishRaceLink(RaceLink):
    link = scrapy.Field(
        input_processor=MapCompose(get_race_id),
        output_processor=TakeFirst()
    )
