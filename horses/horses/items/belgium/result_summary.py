import scrapy
from itemloaders.processors import TakeFirst

from horses.items.base import ResultSummary


class BelgianResultSummary(ResultSummary):
    earnings = scrapy.Field(
        output_processor=TakeFirst()
    )
    mark = scrapy.Field(
        output_processor=TakeFirst()
    )
    seconds = scrapy.Field(
        output_processor=TakeFirst()
    )
    starts = scrapy.Field(
        output_processor=TakeFirst()
    )
    thirds = scrapy.Field(
        output_processor=TakeFirst()
    )
    year = scrapy.Field(
        output_processor=TakeFirst()
    )
    wins = scrapy.Field(
        output_processor=TakeFirst()
    )
