import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_basic, handle_gait, handle_sales_price, convert_to_int


class CanadianAuctionResult(scrapy.Item):
    gait = scrapy.Field(
        input_processor=MapCompose(handle_gait),
        output_processor=TakeFirst()
    )
    hip = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
    horse = scrapy.Field(
        input_processor=MapCompose(dict),
        output_processor=TakeFirst()
    )
    sale = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    sales_price = scrapy.Field(
        input_processor=MapCompose(handle_sales_price),
        output_processor=TakeFirst()
    )
    year = scrapy.Field(
        input_processor=MapCompose(convert_to_int),
        output_processor=TakeFirst()
    )
