import scrapy
from horses.items.base import ResultSummary
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import handle_mark, handle_year


class FrenchResultSummary(ResultSummary):
    mark = scrapy.Field(
        input_processor=MapCompose(handle_mark), output_processor=TakeFirst()
    )
    year = scrapy.Field(
        input_processor=MapCompose(handle_year), output_processor=TakeFirst()
    )
