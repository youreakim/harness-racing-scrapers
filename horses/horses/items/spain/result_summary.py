import scrapy
from horses.items.base import ResultSummary
from itemloaders.processors import MapCompose, TakeFirst

from .processor_functions import (
    convert_to_int,
    handle_basic,
    handle_earnings,
    handle_mark,
    handle_year,
)


class SpanishResultSummary(ResultSummary):
    earnings = scrapy.Field(
        input_processor=MapCompose(handle_earnings),
        output_processor=TakeFirst(),
    )
    mark = scrapy.Field(
        input_processor=MapCompose(handle_basic, handle_mark),
        output_processor=TakeFirst(),
    )
    seconds = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    starts = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    thirds = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    wins = scrapy.Field(
        input_processor=MapCompose(convert_to_int), output_processor=TakeFirst()
    )
    year = scrapy.Field(
        input_processor=MapCompose(handle_year), output_processor=TakeFirst()
    )
