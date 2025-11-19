import scrapy
from itemloaders.processors import TakeFirst, MapCompose

from horses.items.base import ResultSummary
from .processor_functions import handle_mark, handle_year, handle_earnings, handle_placings


class NZResultSummary(ResultSummary):
    earnings = scrapy.Field(
        input_processor=MapCompose(handle_earnings),
        output_processor=TakeFirst()
    )
    mark = scrapy.Field(
        input_processor=MapCompose(handle_mark),
        output_processor=TakeFirst()
    )
    seconds = scrapy.Field(
        input_processor=MapCompose(handle_placings),
        output_processor=TakeFirst()
    )
    starts = scrapy.Field(
        input_processor=MapCompose(handle_placings),
        output_processor=TakeFirst()
    )
    thirds = scrapy.Field(
        input_processor=MapCompose(handle_placings),
        output_processor=TakeFirst()
    )
    wins = scrapy.Field(
        input_processor=MapCompose(handle_placings),
        output_processor=TakeFirst()
    )
    year = scrapy.Field(
        input_processor=MapCompose(handle_year),
        output_processor=TakeFirst()
    )
