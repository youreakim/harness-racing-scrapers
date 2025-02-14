import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import convert_to_float, handle_basic


class RaceStarterOdds(scrapy.Item):
    odds = scrapy.Field(
        input_processor=MapCompose(handle_basic, convert_to_float),
        output_processor=TakeFirst(),
    )
    odds_type = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
