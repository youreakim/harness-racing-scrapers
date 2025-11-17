import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import ResultSummary
from .processor_functions import handle_earnings, handle_mark


class ItalianResultSummary(ResultSummary):
    earnings = scrapy.Field(
        input_processor=MapCompose(handle_earnings),
        output_processor=TakeFirst()
    )
    mark = scrapy.Field(
        input_processor=MapCompose(handle_mark),
        output_processor=TakeFirst()
    )
