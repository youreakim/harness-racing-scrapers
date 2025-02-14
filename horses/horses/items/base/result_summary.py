import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from .processor_functions import handle_basic, convert_to_int


class ResultSummary(scrapy.Item):
    earnings = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    mark = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    seconds = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    starts = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    thirds = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    wins = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    year = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
