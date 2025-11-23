import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RacedayLink
from .processor_functions import get_raceday_id


class SpanishRacedayLink(RacedayLink):
    link = scrapy.Field(
        input_processor=MapCompose(get_raceday_id),
        output_processor=TakeFirst()
    )
