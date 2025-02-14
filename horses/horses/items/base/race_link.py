import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from .processor_functions import handle_basic


class RaceLink(scrapy.Item):
    link = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
    source = scrapy.Field(
        output_processor=TakeFirst()
    )
