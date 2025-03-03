import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import ResultSummary
from .processor_functions import handle_purse, handle_time


class DutchResultSummary(ResultSummary):
    earnings = scrapy.Field(
        input_processor=MapCompose(handle_purse),
        output_processor=TakeFirst()
    )
    mark = scrapy.Field(
        input_processor=MapCompose(handle_time),
        output_processor=TakeFirst()
    )
