import scrapy
from itemloaders.processors import MapCompose, TakeFirst

from horses.items.base import ResultSummary
from .processor_functions import handle_basic


class NorwegianResultSummary(ResultSummary):
    mark = scrapy.Field(
        input_processor=MapCompose(handle_basic),
        output_processor=TakeFirst()
    )
