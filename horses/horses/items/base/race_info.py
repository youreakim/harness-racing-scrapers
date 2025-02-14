import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from .processor_functions import handle_basic, convert_to_int


class RaceInfo(scrapy.Item):
    conditions = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    gait = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    monte = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    racename = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    racenumber = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    racetype = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    startmethod = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    status = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
