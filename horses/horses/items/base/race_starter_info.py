import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import convert_to_int, handle_basic


class RaceStarterInfo(scrapy.Item):
    comment = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    disqualified = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    distance = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    driver = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    finish = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    finished = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    gallop = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    margin = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    order = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    postposition = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    purse = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    started = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
    startnumber = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    trainer = scrapy.Field(
        input_processor=MapCompose(handle_basic), output_processor=TakeFirst()
    )
