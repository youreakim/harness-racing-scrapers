import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from .processor_functions import handle_basic, convert_to_int, convert_to_float


class RaceTime(scrapy.Item):
    at_distance = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    startnumber = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    time = scrapy.Field(
        input_processor=MapCompose(convert_to_float),
        output_processor=TakeFirst()
    )
    time_format = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
