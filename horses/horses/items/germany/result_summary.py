import scrapy
from itemloaders.processors import TakeFirst

from horses.items.base import ResultSummary


class GermanResultSummary(ResultSummary):
    earnings = scrapy.Field(
        output_processor=TakeFirst()
    )
    mark = scrapy.Field(
        output_processor=TakeFirst()
    )
    year = scrapy.Field(
        output_processor=TakeFirst()
    )
