import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import ResultSummary
from .processor_functions import handle_horse_purse, handle_starter_time


class CanadianResultSummary(ResultSummary):
    earnings = scrapy.Field(
        input_processor=MapCompose(handle_horse_purse),
        output_processor=TakeFirst()
    )
    mark = scrapy.Field(
        input_processor=MapCompose(handle_starter_time),
        output_processor=TakeFirst()
    )
