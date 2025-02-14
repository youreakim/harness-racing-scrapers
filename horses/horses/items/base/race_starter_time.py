import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import convert_to_float, convert_to_int, handle_basic


class RaceStarterTime(scrapy.Item):
    from_distance = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    to_distance = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    time = scrapy.Field(
        input_processor=MapCompose(convert_to_float), output_processor=TakeFirst()
    )
    time_format = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
