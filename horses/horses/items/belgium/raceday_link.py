import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import RacedayLink
from .processor_functions import handle_racedaylink


class BelgianRacedayLink(RacedayLink):
    link = scrapy.Field(
        input_processor=MapCompose(handle_racedaylink),
        output_processor=TakeFirst()
    )
