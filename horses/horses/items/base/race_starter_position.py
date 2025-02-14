import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import convert_to_int, handle_basic


class RaceStarterPosition(scrapy.Item):
    position = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    at_distance = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
